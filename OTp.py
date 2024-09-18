import pandas as pd
import streamlit as st
import io


def process_data(mas_file, data_file):
    # Read MAS file
    mas = pd.read_excel(mas_file, sheet_name="Over all")
    mas['TEMPLATE ID'] = mas['TEMPLATE ID'].str.rstrip("'")
    
    # Read data file
    data = pd.read_csv(data_file)
    data['DLTTempID'] = data['DLTTempID'].astype(str)
    
    # Merge data
    merged_data = pd.merge(data, mas, left_on='DLTTempID', right_on='TEMPLATE ID', how='left')
    merged_data = merged_data.rename(columns={'TEMPLATE NAME': 'template_name'})
    data['template_name'] = merged_data['template_name'].values
    
    # Perform pivot and calculations
    pivot_tot_count = pd.pivot_table(data, index='template_name', columns='Status', values='SMSCount', aggfunc='sum', margins=True, margins_name='Total')
    pivot_sms_count = pd.pivot_table(data, index='template_name', values='SMSCount', aggfunc='sum', margins=True, margins_name='Total')
    pivot_table = pd.concat([pivot_tot_count, pivot_sms_count], axis=1)
    pivot_table['Delivered_Percentage'] = pivot_table['D'] / pivot_table['Total'] * 100

    # Rename columns
    column_mapping = {'D': 'Delivered', 'S': 'Submitted', 'R': 'Reversed', 'I': 'Invalid', 'F': 'Failed'}
    pivot_table.rename(columns=column_mapping, inplace=True)
    
    return pivot_table

def main():
    st.title('OTP status')

    # Upload MAS file
    st.header('Upload template_master File')
    mas_file = st.file_uploader("Upload template_master Excel file", type=['xlsx'])
    
    # Upload Data file
    st.header('Upload OTP Data File')
    data_file = st.file_uploader("Upload OTP Data CSV file", type=['csv'])
    
    if mas_file is not None and data_file is not None:
        if st.button('Generate Output'):
            output_data = process_data(mas_file, data_file)
            # Save output to Excel file
            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
                output_data.to_excel(writer, sheet_name='Pivot_Table')
            output_buffer.seek(0)
            st.write("Output generated successfully!")
            st.write("Download the output file below:")
            st.download_button(label="Download Output Excel", data=output_buffer, file_name="output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
