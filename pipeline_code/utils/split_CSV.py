import pandas as pd
import os

def split_CSV(input_file, max_mb_size = 50):                                    # function to split CSV > 50MB into smaller files < 50MB for database purposes 
    df = pd.read_excel(input_file)                                              # load file into df

    df = df.rename(columns = {                                                  # rename columns to match PostgreSQL table
        "Title": "title",
        "Director": "director",
        "Cast": "cast",
        "Genre": "genre",
        "Plot": "plot",
        "Release Date": "release_date",
        "Slug": "slug",
        "Poster Filename": "poster_filename",
        "Processed_Plot": "processed_plot",
        "Pre_genre": "pre_genre",
        "Pre_director": "pre_director",
        "Pre_cast": "pre_cast"
    })

    # calculate num of rows per file to check that file is under max size limit
    row_count = len(df)
    max_size = max_mb_size * 1024 * 1024
    approx_row_size = df.memory_usage(deep = True).sum() / row_count            # estimate average size of a row
    rows_per_file = int(max_size/approx_row_size)

    num_chunks = (row_count//rows_per_file) + 1                                 # split df into chunks of rows 

    output_dir = os.path.join('data', 'split_CSV')                              # define directory where CSV files will be saved 
    os.makedirs(output_dir, exist_ok = True)                                    # create directory inside data folder 

    for i in range(num_chunks):
        start = i * rows_per_file                                               # determine start index for chunk
        end = (i + 1) * rows_per_file                                           # determine end index for chunk

        chunk = df[start:end]                                                   # get chunk of data 

        # write chunk to new CSV file
        output_file = os.path.join(output_dir, f"CSV_chunk_{i + 1}.csv")
        chunk.to_csv(output_file, index = False)

if __name__ == "__main__":
    input_csv_file =  '../data/processed/spreadsheets/3_preprocessed_dataset.xlsx'
    split_CSV(input_csv_file, max_mb_size = 50)
