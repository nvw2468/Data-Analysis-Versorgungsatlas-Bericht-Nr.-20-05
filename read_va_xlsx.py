# Here we define a function that will read dat from csvs files that can be downloaded from the following source:
# Source:
# Bätzing J, Holstiege J, Hering R, Akmatov MK, Steffen A, Dammertz L, Czihal T, von Stillfried D.
# Häufigkeiten von Vorerkrankungen mit erhöhtem Risiko für einen schwerwiegenden klinischen Verlauf von COVID-19 – Eine Analyse kleinräumiger Risikoprofile in der deutschen Bevölkerung.
# Zentralinstitut für die kassenärztliche Versorgung in Deutschland (Zi).
# Versorgungsatlas-Bericht Nr. 20/05.
#Berlin 2020
# DOI: 10.20364/VA-20.05
# Link: https://www.versorgungsatlas.de/themen/alle-analysen-nach-datum-sortiert/?tab=2&uid=110

# If you are considering how to automatically download files (with different filters) - please refer to my scrpit "00_Dataimport"
import os
import pandas as pd
def read_va_xlsx(filepath):
   
    if (os.path.exists(filepath) and os.path.isfile(filepath)):
        # Reading the metadata
        # This information is listed on the first sheet named "Hintergrundinformationen"
        # At the end we will load the metadata as a dictionary
        xl = pd.ExcelFile(filepath)
        df_metadata = pd.read_excel(filepath, sheet_name="Hintergrundinformationen")
        # In pandas versions  0.20 and prior,
        # this was sheetname rather than sheet_name (this is now deprecated in favor of the above)
        df_metadata.iloc[0,1]=df_metadata.iloc[0,0]
        df_metadata.iloc[0,0]='Metadata Inhalt'
        df_metadata.iloc[5,1]=df_metadata.iloc[5,0]
        df_metadata.iloc[5,0]='Wichtiger Hinweis'
        df_metadata.columns =['Property','Value']
        new_row=[]
        new_row.insert(0, {'Property': 'Language', 'Value': 'DE'})
        df_metadata=pd.concat([pd.DataFrame(new_row), df_metadata], ignore_index=True)
        df_metadata.index=df_metadata['Property']
        df_metadata=df_metadata.drop(columns=['Property'])
        metadata_dictionary=df_metadata.to_dict()
        metadata_dictionary=metadata_dictionary['Value']
        
        #Reading the real data
        df_data = pd.read_excel(filepath, sheet_name="Daten",skiprows=range(0,3),header=0,thousands=".",decimal=",")
        df_data_metadata=pd.read_excel(filepath, sheet_name="Daten",header=None,usecols="A:A").head(2)
        # Formatting the columns
        df_data["Wert"]=pd.to_numeric(df_data["Wert"])
        #Generating columns for chosen filter values
        filter_sentence=df_data_metadata.iloc[0,0]
        not_nan_count_sentence=df_data_metadata.iloc[1,0]
        not_nans_total_string=not_nan_count_sentence.replace('Gültige Werte für: ','') 
        not_nans_total_string=not_nans_total_string.split(" von ")
        valid_values_count=int(not_nans_total_string[0])
        total_rows=int(not_nans_total_string[1].split(" ")[0])
        df_data_rows=len(df_data)
        df=pd.DataFrame()
        filter_sentence=filter_sentence.replace("Ihre Auswahl: ", "")
        filter_sentence=filter_sentence.replace(" ", "")
        auspraegungs_wert_ix=filter_sentence.find("Ausprägungswert")
        auspraegungs_wert_filter=filter_sentence[auspraegungs_wert_ix:]
        filter_name='Ausprägungswert'
        filter_value=auspraegungs_wert_filter.replace("Ausprägungswert-", "")
        filter_col= [filter_value ]*df_data_rows
        df[filter_name]=filter_col
        filter_sentence=filter_sentence[0: auspraegungs_wert_ix-1]        
        filters=filter_sentence.split(",")        
        for pair_name_value in filters:
            name_value=pair_name_value.split('-')
            filter_name=name_value[0]
            filter_value=name_value[1]
            if filter_name =='Region':
                filter_name='Region_Type' 
            filter_col= [filter_value ]*df_data_rows
            df[filter_name]=filter_col
            if(filter_name!='Wert'):
                df[filter_name]=str(df[filter_name])
        df_data=pd.concat([df_data,df], axis=1)     
        #Checking if read data with the statement are correct
        print("In the file it was stated that there are "+str(total_rows)+" which of "+str(valid_values_count)+" should be with valid value.")
        return metadata_dictionary,df_data
    else:
        print('The file does not exist')
        return -1