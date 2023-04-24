import PyPDF2
import tabula
import pandas as pd

from helpers.utils import drop_columns_to_rows, drop_columns_with_nan

file_name = "Kumon_Recommended_Reading_List.pdf"

# Open the PDF file in read-binary mode
with open(file_name, 'rb') as file:
    # Create a PDF reader object
    reader = PyPDF2.PdfReader(file)
    # Get the total number of pages in the PDF document
    num_pages = len(reader.pages)

# Initialize an empty list to store the extracted data
data = []
levels = {"0": ["level_7a", "level_6a", "level_5a", "level_4a", "level_3a"],
          "1": ["level_7a", "level_6a", "level_5a", "level_4a", "level_3a"],
          "2": ["level_2a", "level_A1", "level_A2", "level_B1", "level_B2"],
          "3": ["level_C1", "level_C2", "level_D", "level_E", "level_F"],
          "4": ["level_G", "level_H", "level_I"],
          "5": ["level_J", "level_K", "level_L"]}

maindf = pd.DataFrame()
# Loop through each page of the PDF document
for i in range(num_pages):
    # Read the table from each page of the PDF document using tabula-py
    tables = tabula.read_pdf(file_name, pages=i+1, multiple_tables=True, lattice=True)
    for j, table in enumerate(tables):
        try:
            if (i == 3) & (j == 0):
                table = drop_columns_with_nan(table, 0.7)
            table.dropna(inplace=True)
            table.reset_index(drop=True, inplace=True)


            # create a row from the column indices if there is no Unnamed: 1 column
            if 'Unnamed: 1' not in table.columns:
                table = drop_columns_to_rows(table, ['Unnamed: 0', 'Unnamed: 1'])

            if (i!=3) & (j!=0):
                table.rename(columns={'Unnamed: 1': 'book_details'}, inplace=True)
            else:
                table.rename(columns={'Unnamed: 3': 'book_details'}, inplace=True)

            # within the book_details column split the title and author into separate columns and drop the book_details column
            table = table.book_details.str.split("\\r", expand=True)

            # rename the 0 column to book_title, combine rest of the columns into a single column with , and rename it to author
            table.rename(columns={0: 'title'}, inplace=True)
            table['author'] = table.iloc[:, 1:].apply(lambda x: ', '.join(x.dropna().astype(str)), axis=1)

            # just keep the title and author column, drop the rest
            table = table[['title', 'author']]

            # remove the extra spaces from the title and author columns
            table['title'] = table['title'].str.strip()
            table['author'] = table['author'].str.strip()
            table['level'] = levels[str(i)][j]
            # add the table to the main dataframe
            if len(maindf) == 0:
                maindf = table.copy()
            else:
                maindf = pd.concat([maindf, table], ignore_index=True)
        except Exception as e:
            print("Problem with page: ", i, " and table: ", j)
            print(e)

# Print the final dataframe
print(maindf)
maindf.to_csv("book_levels.csv", index=False)