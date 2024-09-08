import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.express as px
from datetime import datetime
import pandas as pd
import plotly.express as px

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.secret_key = 'supersecretkey'  # for flashing messages


DATA_PATH = 'data/patients_data.csv'

# Function to check allowed file types
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
        
#         file = request.files['file']
        
#         # If the user does not select a file, browser also submits an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
        
#         # If file is allowed, save it to the 'data' folder
#         if file and allowed_file(file.filename):
#             filename = file.filename
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
            
#             # Process the uploaded file
#             return redirect(url_for('dashboard', filename=filename))
    
#     return render_template('upload.html')

@app.route('/')
def dashboard():
    # Load the uploaded CSV file into a Pandas DataFrame
    # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # df = pd.read_csv(file_path)

    # Load the preloaded CSV file into a Pandas DataFrame
    df = pd.read_csv(DATA_PATH)

    # Initialize graph_html to prevent UnboundLocalError
    graph_html = None
    age_distribution_html = None
    patient_scan_history_html = None
    patient_scan_facet_html = None
    doughnut_race_html = None  # New variable for the doughnut plot

    # Calculate total patients (number of unique GUIDs)
    total_patients = None
    if 'Guid' in df.columns:
        total_patients = df['Guid'].nunique()

    # Calculate total number of scans (number of rows in the CSV)
    total_scans = len(df)

    # Calculate average scans per month
    avg_scans_per_month = None
    if 'Date' in df.columns:
        # Convert to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        
        # Group by year and month
        df['YearMonth'] = df['Date'].dt.to_period('M')
        scans_per_month = df.groupby('YearMonth').size()

        # Calculate the average scans per month
        avg_scans_per_month = scans_per_month.mean()
        
    else:
        avg_scans_per_month = "N/A"  # Handle missing Date column

    # 1. AGE DISTRIBUTION BAR PLOT (Patient)

    # Generate age distribution bar plot using Birthdate (same as before)
    if 'Birthdate' in df.columns:
        df['Birthdate'] = pd.to_datetime(df['Birthdate'], errors='coerce')
        df.dropna(subset=['Birthdate'], inplace=True)

        # Calculate age
        current_year = datetime.now().year
        df['Age'] = current_year - df['Birthdate'].dt.year

        # Create age bins
        age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        age_labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']
        df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)

        # Count the number of individuals in each age group
        age_group_counts = df['AgeGroup'].value_counts().sort_index().reset_index()
        age_group_counts.columns = ['AgeGroup', 'Count']

        # Create a bar plot
        fig_age = px.bar(age_group_counts, x='AgeGroup', y='Count', title='AGE DISTRIBUTION',  color_discrete_sequence=['#2B5783'], labels={'AgeGroup': 'AGE RANGE', 'Count': 'NR OF PEOPLE'})
        fig_age.update_layout(
            font=dict(family="Montserrat, sans-serif", size=14),
            width=None,  # Let the container dictate the width
            height=None,  # Let the container dictate the height
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plotting area
            paper_bgcolor= '#e3f0fb',
            yaxis=dict(
            gridcolor='#4A4D4F',  # Light blue gridlines on y-axis
            )
        )

        # Convert the plot to HTML
        age_distribution_html = fig_age.to_html(full_html=False)

    # 2.DOUGHNUT CHART FOR PROPORTION OF RACES

    # Generate a doughnut chart for proportion of races
    if 'Race' in df.columns:
        # Filter to unique instances of Guid
        unique_patients = df.drop_duplicates(subset=['Guid'])

        # Calculate the proportion of races
        race_data = unique_patients['Race'].value_counts().reset_index()
        race_data.columns = ['Race', 'Count']

        # Create a doughnut chart (which is just a pie chart with a hole in the center)
        fig_doughnut = px.pie(race_data, names='Race', values='Count', title='PROPORTION OF PATIENTS BY RACE', hole=0.4)  # hole=0.4 makes it a doughnut chart

        # Update layout for readability
        fig_doughnut.update_layout(
            font=dict(family="Montserrat, sans-serif", size=14),
            legend_title="Race",
            width=500,
            height=None,
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plotting area
            paper_bgcolor= '#e3f0fb',
        )

        # Convert the doughnut plot to HTML
        doughnut_race_html = fig_doughnut.to_html(full_html=False)

    # 3. DISTRIBUTION OF SCAN VALUES PER GENDER
    # Generate a plot for the distribution of "Value" column based on "Sex" (Males and Females)
    if 'Value' in df.columns and 'Sex' in df.columns:
    # Create a density plot for the distribution of "Value" grouped by "Sex"
        fig_distribution = px.histogram(
            df, 
            x='Value', 
            color='Sex', 
            marginal='box',  # Adds a box plot on the margin for better distribution view
            title='DISTRIBUTION OF SCAN VALUES BY SEX', 
            labels={'Value': 'SCAN VALUE'},
            nbins=30,  # Adjust the number of bins
            color_discrete_map={'Male': '#44709C', 'Female': 'pink'}  # Custom colors for Males and Females
        )

    # Update layout for better readability
    fig_distribution.update_layout(
        font=dict(family="Montserrat, sans-serif", size=14),
        xaxis_title='SCAN VALUE',
        yaxis_title='COUNT',
        autosize=True,
        width=None,
        height=None,
        #margin=dict(l=10, r=10, t=50, b=10), # Adjust margins to remove unnecessary padding
        legend_title= "GENDER",
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plotting area
        paper_bgcolor= '#e3f0fb',
        yaxis=dict(
        gridcolor='#4A4D4F')
    )

    # Convert the plot to HTML
    value_distribution_html = fig_distribution.to_html(full_html=False)

    # 4. DENSITY PLOT OF SCAN VALUES PER RACE
   # Generate a density plot for the distribution of "Value" column based on "Race"
    if 'Value' in df.columns and 'Race' in df.columns:
    # Create a density plot for the distribution of "Value" grouped by "Race"
        fig_density = px.violin(
            df, 
            x='Value', 
            color='Race', 
            box=True,  # Add a box plot inside the violin
            points='all',  # Show all points on the violin plot
            title='DENSITY PLOT OF SCANED VALUES BY RACE', 
            labels={'Value': 'Scan Value'},
            color_discrete_sequence=px.colors.qualitative.Set2  # Set custom color scheme for races   
        )

    # Update layout for better readability
        fig_density.update_layout(
            font=dict(family="Montserrat, sans-serif", size=14),
            xaxis_title='SCAN VALUES',
            yaxis_title='DENSITY',
            autosize=True,
            width=None,
            height=None,
            legend_title="RACE",
            #margin=dict(l=10, r=10, t=50, b=10) # Adjust margins to remove unnecessary padding
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plotting area
            paper_bgcolor= '#e3f0fb'
        )

    # Convert the plot to HTML
    value_density_html = fig_density.to_html(full_html=False)

    # 5. PATIENT'S SCAN VALUE HISTORY (FACETED)
    # Generate a facet grid for patient's scan value history by Nationality
    if 'Guid' in df.columns and 'Date' in df.columns and 'Value' in df.columns and 'Nationality' in df.columns:
        # Ensure Date is in datetime format
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Create a facet line chart where each facet represents a different Nationality
        fig_facet = px.line(df, x='Date', y='Value', color='Guid', facet_row='Nationality', title="PATIENTS SCAN VALUES PER NATIONALITY", labels={'Date': 'SCAN DATE', 'Value': 'SCAN VALUE'})
        
        # Update layout for readability and set height for the stacked plot
        fig_facet.update_layout(
        font=dict(family="Montserrat, sans-serif", size=14),
        xaxis_title='DATE',
        yaxis_title='SCAN VALUE',
        showlegend=False,  # Hide the legend
        autosize=True,
        width=1200,
        height=1500,
        margin=dict(l=10, r=10, t=50, b=10), # Adjust margins to remove unnecessary padding
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for the plotting area
        paper_bgcolor= '#e3f0fb',
        yaxis=dict(
        gridcolor='#4A4D4F')
        )

        # Remove the y-axis label
        fig_facet.update_yaxes(title_text='')

        # Customize facet labels to only show the race (without "Nationality=")
        fig_facet.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        # Convert the facet plot to HTML
        patient_scan_facet_html = fig_facet.to_html(full_html=False)


    # Pass all values and charts to the template
    return render_template('dashboard.html', 
                           #graph_html=graph_html, 
                           total_patients=total_patients, #value box 1
                           total_scans=total_scans, #value box 2
                           avg_scans_per_month=avg_scans_per_month, #value box 3
                           age_distribution_html=age_distribution_html, # bar plot
                           doughnut_race_html=doughnut_race_html, # donut plot
                           value_density_html=value_density_html, # gender density plot
                           value_distribution_html=value_distribution_html, # value distribution per race
                           patient_scan_facet_html=patient_scan_facet_html # facet plot
                           )

if __name__ == '__main__':
    #if not os.path.exists(app.config['UPLOAD_FOLDER']):
    #    os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
