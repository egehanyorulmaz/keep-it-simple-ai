import csv

input_file = 'book_levels_manual_fixed.csv'
output_file = 'book_levels_comma_fixed.csv'

with open(input_file, 'r', newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='',
                                                                         encoding='utf-8') as outfile:
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=',')

    for row in reader:
        writer.writerow(row)