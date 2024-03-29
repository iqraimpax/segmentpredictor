from azure.storage.blob import BlobServiceClient
import warnings
import io
# Suppress all warnings
warnings.filterwarnings("ignore")
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
connection_string = 'DefaultEndpointsProtocol=https;AccountName=impaxhkstorage;AccountKey=JP0AK1g5wtimYcuUZy9R3rIXi/A9qLIx/grnzzC9sliXnAwalR23EH1V//CVQaTakyXFKoyU7IOy+AStq/5hCQ==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = 'stocksplit'
container_client = blob_service_client.get_container_client(container_name)
from datetime import datetime
columns = ['Index', 'Company','Segment', 'Segment Description', 'text', 'Predicted', 'Corrected']

# Create the DataFrame
corrected = pd.DataFrame(columns=columns)

# Add current date and time to the DataFrame name
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
blob_name = f"corrected_{current_datetime}.csv"

i=0
dropdown_value = None
options = ['Not Applicable', 'Energy Management & Efficiency', 'Alternative Energy', 'Sustainable Food & Agriculture', 'Digital Infrastructure', 'Transport Solutions', 'Resource Efficiency & Waste Management', 'Environmental Services & Resources', 'Water Infrastructure & Technologies'] 

df=pd.read_csv('input_for_seg_predictor.csv')
df = df.sample(frac=1)
app = dash.Dash(__name__)

app.layout = html.Div(
    style={'font-family': 'Arial, sans-serif','width': '75vw'},
    children=[
        html.P('The following shows Segments and Descriptions of various companies, along with their predicted EM value'),
        html.P('   '),
        html.Table(
            style={'border': '1px solid #ccc', 'border-collapse': 'collapse', 'width': '100%'},
            children=[
                html.Thead(
                    style={'background-color': '#f2f2f2'},
                    children=[
                        html.Tr(
                            children=[
                                html.Th('Index', style={'padding': '8px', 'border': '1px solid #ccc'}),
                                html.Th('Company', style={'padding': '8px', 'border': '1px solid #ccc'}),
                                html.Th('Segment', style={'padding': '8px', 'border': '1px solid #ccc'}),
                                html.Th('Segment Description', style={'padding': '8px', 'border': '1px solid #ccc'}),
                                html.Th('Prediction', style={'padding': '8px', 'border': '1px solid #ccc'})
                            ]
                        )
                    ]
                ),
                html.Tbody(id='table-body')
            ]
        ),
        
        html.P('Click Next if the prediction is right'),
        html.P(''),
        html.Button('Next Row', id='next-button', n_clicks=0),
       
        html.P('Or if the prediction is wrong, select from the dropdown list'),
        html.P(''),
        dcc.Dropdown(
            id='dropdown',
            options=options,
            value=None
        ),
        html.P(''),
        html.Button('Confirm change', id='confirm-button', n_clicks=0),
        html.P(''),
        html.Button('Save and Close', id='save-close-button',style={'color': 'red'}),
        html.P('', id='save-close-button-message', style={'color': 'red'})

    ]
)


@app.callback(
    Output('table-body', 'children'),
    [Input('next-button', 'n_clicks'), Input('confirm-button', 'n_clicks')],
    [State('dropdown', 'value')]
)
def update_table(n_clicks_next, n_clicks_confirm, dropdown_value):
    global i
    global corrected
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'confirm-button' and dropdown_value is not None:
        current_row = df.iloc[i]
        input_str = df.iloc[i, :].tolist()

        new_row = html.Tr([
           html.Td(
               current_row.name,
               style={'padding': '10px'}
           ),
           html.Td(
               current_row['Company'], 
               style={'padding': '10px'}
           ),
           html.Td(
               current_row['Segment'],
               style={'padding': '10px'} 
           ),
           html.Td(
               current_row['Segment Description'],
               style={'padding': '10px'}
           ), 
           html.Td(
               current_row['Predicted'],
               style={'padding': '10px'}
           )
        ])
        current_row = df.iloc[i-1]
        new_row_values = [current_row.name, current_row['Company'], current_row['Segment'], current_row['Segment Description'], current_row['text'], current_row['Predicted'], dropdown_value]
        print(new_row_values)
        
        corrected.loc[len(corrected)] = new_row_values
        #updated_content = corrected.to_csv(blob_name, index=False)
        #container_client.upload_blob(blob_name, corrected.to_csv(), overwrite=True)


        print("New row added and saved to Azure Blob Storage.")

        i += 1

    else:
        current_row_index = i
        current_row = df.iloc[current_row_index]

        new_row = html.Tr([
           html.Td(
               current_row.name,
               style={'padding': '10px'}
           ),
           html.Td(
               current_row['Company'], 
               style={'padding': '10px'}
           ),
           html.Td(
               current_row['Segment'],
               style={'padding': '10px'} 
           ),
           html.Td(
               current_row['Segment Description'],
               style={'padding': '10px'}
           ), 
           html.Td(
               current_row['Predicted'],
               style={'padding': '10px'}
           )
        ])
        current_row = df.iloc[i-1]
        new_row_values = [current_row.name, current_row['Company'], current_row['Segment'], current_row['Segment Description'], current_row['text'], current_row['Predicted'], current_row['Predicted']]
        print(new_row_values)
        
        corrected.loc[len(corrected)] = new_row_values
        #updated_content = corrected.to_csv(blob_name, index=False)
        #container_client.upload_blob(blob_name, corrected.to_csv(), overwrite=True)


        print("New row added and saved to Azure Blob Storage.")

        i += 1
        

    return new_row



if __name__ == '__main__':
    app.run_server(debug=True,port=8051)


# Define the callback function to update the message
@app.callback(
    Output('save-close-button-message', 'children'),
    [Input('save-close-button', 'n_clicks')]
)
def save_and_close(n_clicks):
    if n_clicks:
        container_client.upload_blob(blob_name, corrected.to_csv(), overwrite=True)
        return "Saved - you can now close this window"
    
    #return ""




