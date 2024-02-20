import pandas as pd
import query
from pendulum import today
from PySimpleGUI import popup_get_file, popup_get_folder
from dateutil.parser import parse

# def contains_date(string, fuzzy=True):
#     """
#     Return whether the string can be interpreted as a date.
#
#     :param string: str, string to check for date
#     :param fuzzy: bool, ignore unknown tokens in string if True
#     """
#     try:
#         parse(string, fuzzy=fuzzy)
#         return True
#
#     except ValueError:
#         return False

file_path_n = "CDI_TRANSACTION_ASSISTANT_EXPORT_RET_20220604054331.CSV"
hrs_file_name_n = ""

lab_file_name_n = ""
# 510510
date = today().strftime("%Y%m%d")

def process_cdi_errors_today(file_path, output_path, hrs_file_name=("HRS_Backlogs_" + date + ".csv"), lab_file_name=("Labour_BAU_Backlogs_" + date + ".csv")) :
    df = pd.read_csv(file_path, encoding="cp1252")

    rows = df.shape[0]

    df["COLLEAGUE ID"].fillna("0", inplace=True)
    try : df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("int")
    except ValueError : pass
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("string")

    # df['COLLEAGUE ID'] = df['COLLEAGUE ID'].str.replace(".0", "")
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].replace("0", "", limit=1)

    df['DESCRIPTION'] = df['DESCRIPTION'].astype("string")
    df["DESCRIPTION"].fillna("", inplace=True)

    df['ERROR DATE & TIME'] = pd.to_datetime(df['ERROR DATE & TIME']).dt.date

    df['FIELD NAME ERROR'] = df['FIELD NAME ERROR'].astype("string")
    df["FIELD NAME ERROR"].fillna("", inplace=True)

    df['ID'] = df['ID'].astype("string")
    df["ID"].fillna("", inplace=True)

    df['TRANSACTION TYPE'] = df['TRANSACTION TYPE'].astype("string")
    df["TRANSACTION TYPE"].fillna("", inplace=True)

    # Reordering the table columns
    df = df[["COLLEAGUE ID", "ERROR DATE & TIME", "DESCRIPTION", "TRANSACTION TYPE", "ERROR NUMBER", "FIELD NAME ERROR", "ID" ]]

    # Adding Summary and Teams & Actions columns; Data filled through function
    df["Summary"]        = [query.get_summary(row["DESCRIPTION"], row["TRANSACTION TYPE"]) for index, row in df.iterrows()]
    df["Team & Actions"] = [query.get_team_and_action(row["Summary"]) for index2, row in df.iterrows()]

    # df = df.sort_values(by=['Team & Actions'])


    # This one actually doesnt work as iterrows works on copy of df. so use {df.at[index, column] = value} to modify values
    others  = df[df["Team & Actions"].str.contains('Review and Assign to HRS or Labour')]
    for index, row in others.iterrows():
        print(row)
        while True :
            print("\nSelect Option Number :")
            print("1. HRS | 2. Labour BAU | 3. Ignore")
            val = int(input("Enter a value"))
            print("Entered value :", val, "|")
            if val == 1 :
                row['Team & Actions'] = "HRS to action."; break
            elif val == 2 :
                row['Team & Actions'] = "Labour BAU to action."; break
            elif val == 3 :
                row['Team & Actions'] = "Ignore."; break
            else : print("Wrong value : Try Again")

    hrs = df[df["Team & Actions"].str.contains('HRS')]
    lab_bau = df[df["Team & Actions"].str.contains('Labour')]
    # print(df.shape[0])
    print(df.info())
    print("1")
    print(df.to_string())
    print("\n\n2 : HRS")
    print(hrs.to_string(), "\n")
    print("\n3 : Labour BAU")
    print(lab_bau.to_string(), "\n")
    print("\n4 : Unprocessed / To be reviewed :")
    print(others.to_string(), "\n")
    print("5")

    # hrs = hrs.drop(hrs.index[1])
    # lab_bau = lab_bau.drop(lab_bau.index[1])
    # data = data.drop(data.index[1])
    if len(output_path) > 0 :
        hrs.to_csv(output_path + "/" + hrs_file_name, index=False)
        lab_bau.to_csv(output_path + "/" + lab_file_name, index=False)
    else :
        hrs.to_csv(hrs_file_name, index=False)
        lab_bau.to_csv(lab_file_name, index=False)

def process_cdi_errors_date(file_path, date, hrs_file_name="HRS_Backlogs_", lab_file_name="Labour_BAU_Backlogs_") :
    df = pd.read_csv(file_path, encoding="cp1252")

    rows = df.shape[0]

    df["COLLEAGUE ID"].fillna(0, inplace=True)
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("int")
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("string")
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].replace("0", "")

    df['DESCRIPTION'] = df['DESCRIPTION'].astype("string")
    df["DESCRIPTION"].fillna("", inplace=True)

    df['ERROR DATE & TIME'] = pd.to_datetime(df['ERROR DATE & TIME']).dt.date

    df['FIELD NAME ERROR'] = df['FIELD NAME ERROR'].astype("string")
    df["FIELD NAME ERROR"].fillna("", inplace=True)

    df['ID'] = df['ID'].astype("string")
    df["ID"].fillna("", inplace=True)

    df['TRANSACTION TYPE'] = df['TRANSACTION TYPE'].astype("string")
    df["TRANSACTION TYPE"].fillna("", inplace=True)

    # Reordering the table columns
    df = df[["COLLEAGUE ID", "ERROR DATE & TIME", "DESCRIPTION", "TRANSACTION TYPE", "ERROR NUMBER", "FIELD NAME ERROR", "ID" ]]

    # Adding Summary and Teams & Actions columns; Dat filled through function
    df["Summary"]        = [query.get_summary(row["DESCRIPTION"], row["TRANSACTION TYPE"]) for index, row in df.iterrows()]
    df["Team & Actions"] = [query.get_team_and_action(row["Summary"]) for index2, row in df.iterrows()]

    df = df.sort_values(by=['Team & Actions'])

    hrs     = df[df["Team & Actions"].str.contains('HRS')]
    lab_bau = df[df["Team & Actions"].str.contains('Labour')]
    others  = df[df["Team & Actions"].str.contains('Review and Assign to HRS or Labour')]
    # print(df.shape[0])
    print(df.info())
    print(df.to_string())

    print(hrs.to_string(), "\n")
    print(lab_bau.to_string(), "\n")
    print(others.to_string(), "\n")

    hrs.to_csv(hrs_file_name+date+".csv")
    lab_bau.to_csv(lab_file_name+date+".csv")

def process_cdi_errors_date_from_name(file_path, date, hrs_file_name="HRS_Backlogs_", lab_file_name="Labour_BAU_Backlogs_") :


    df = pd.read_csv(file_path, encoding="cp1252")

    rows = df.shape[0]

    df["COLLEAGUE ID"].fillna(0, inplace=True)
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("int")
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].astype("string")
    df['COLLEAGUE ID'] = df['COLLEAGUE ID'].replace("0", "")

    df['DESCRIPTION'] = df['DESCRIPTION'].astype("string")
    df["DESCRIPTION"].fillna("", inplace=True)

    df['ERROR DATE & TIME'] = pd.to_datetime(df['ERROR DATE & TIME']).dt.date

    df['FIELD NAME ERROR'] = df['FIELD NAME ERROR'].astype("string")
    df["FIELD NAME ERROR"].fillna("", inplace=True)

    df['ID'] = df['ID'].astype("string")
    df["ID"].fillna("", inplace=True)

    df['TRANSACTION TYPE'] = df['TRANSACTION TYPE'].astype("string")
    df["TRANSACTION TYPE"].fillna("", inplace=True)

    # Reordering the table columns
    df = df[["COLLEAGUE ID", "ERROR DATE & TIME", "DESCRIPTION", "TRANSACTION TYPE", "ERROR NUMBER", "FIELD NAME ERROR", "ID" ]]

    # Adding Summary and Teams & Actions columns; Dat filled through function
    df["Summary"]        = [query.get_summary(row["DESCRIPTION"], row["TRANSACTION TYPE"]) for index, row in df.iterrows()]
    df["Team & Actions"] = [query.get_team_and_action(row["Summary"]) for index2, row in df.iterrows()]

    df = df.sort_values(by=['Team & Actions'])

    hrs     = df[df["Team & Actions"].str.contains('HRS')]
    lab_bau = df[df["Team & Actions"].str.contains('Labour')]
    others  = df[df["Team & Actions"].str.contains('Review and Assign to HRS or Labour')]
    # print(df.shape[0])
    print(df.info())
    print(df.to_string())

    print(hrs.to_string(), "\n")
    print(lab_bau.to_string(), "\n")
    print(others.to_string(), "\n")

    hrs.to_csv(hrs_file_name+date+".csv")
    lab_bau.to_csv(lab_file_name+date+".csv")



process_cdi_errors_today(popup_get_file("Select input CDI file : "), popup_get_folder("Select output folder : "))

# hr_errors_path = popup_get_file("Select HR Source errors file : ")
# transformed_source_data_path = popup_get_file("Select Transformed source data file : ")
#
# output_zip_path = PySimpleGUI.popup_get_folder("Select output path : ")
# output_file_name = "/CDI_Errors_Retail_" + date
# output_zip_path += output_file_name
#
# hrs_file_name=("HRS_Backlogs_" + date + ".csv")
# lab_file_name=("Labour_BAU_Backlogs_" + date + ".csv")
#
# import shutil
#
# shutil.move(hr_errors_path, (output_zip_path + "/" + hr_errors_path.split("/")[-1]))
# shutil.move(transformed_source_data_path, (output_zip_path + "/" + transformed_source_data_path.split("/")[-1]))
# shutil.move(hrs_file_name, (output_zip_path + "/" + hrs_file_name))
# shutil.move(lab_file_name, (output_zip_path + "/" + lab_file_name))
#
# import os
# import zipfile
#
#
# def zipdir(path, ziph):
#     # ziph is zipfile handle3
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(os.path.join(root, file),
#                        os.path.relpath(os.path.join(root, file),
#                                        os.path.join(path, '..')))
#
#
# with zipfile.ZipFile(output_file_name + ".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zipdir(output_zip_path + "/", zipf)
