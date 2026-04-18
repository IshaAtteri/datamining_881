// convert excel dataset to JSON for easier parsing & easier deployment
const XLSX = require("xlsx");
const fs = require("fs");
const path = require("path");

const filePath = path.join(__dirname, "../preprocessed_data.xlsx")          // path to excel file -- change this path to be spreadsheets\updated_datav2.xlsx
// const filePath = path.join(__dirname, "../spreadsheets/updated_datav2.xlsx")        // path to excel file 
const workbook = XLSX.readFile(filePath);                                   // read excel workbook

const sheetName = workbook.SheetNames[0];                                   // get first sheet 
const sheet = workbook.Sheets[sheetName];

const rawData = XLSX.utils.sheet_to_json(sheet);                            // convert to JSON

const cleanedData = rawData.map((movie) => ({                               // transform data 
    title: movie.Title,
    director: movie.Director || "",
    cast: movie.Cast || "",
    genre: movie.Genre || "",
    plot: movie.Plot || "",
    releaseDate: movie["Release Date"] || "",
    slug: movie.Slug || "",
    poster: movie["Poster Filename"]
        ? `/posters/${movie["Poster Filename"]}`
        : null,
}));

fs.writeFileSync(path.join(__dirname, "../movies.json"), JSON.stringify(cleanedData, null, 2));

// to run: node scripts/convertExcelToJson.js