# Reaction Analysis Project

## Overview

This repository contains the code and data used for analyzing chemical reactions. The code and data support the article published in the *Journal of Chemical Information and Modeling*, titled "A Postprocessing Tool for Efficient Molecular Reaction Path Analysis in Kinetic Simulations", with the article link: [https://pubs.acs.org/doi/10.1021/acs.jcim.5c01229](https://pubs.acs.org/doi/10.1021/acs.jcim.5c01229).

## Features

- **Data Preprocessing**: Cleansing and formatting raw chemical data.
- **Reaction Analysis**: Analyzing patterns and trends in chemical reactions.
- **Result Visualization**: Displaying analysis results in graphical form.

## Usage

### 1. Install Dependencies
Ensure your system has the following dependencies installed:
- Python 3.x
- NumPy
- Pandas
- Matplotlib
- Any other libraries that might be required.
In addition, you will need to prepare the Graphviz tool. If you do not have it, you can find it in the package/Graphviz folder.

You can install these dependencies by running:
```bash
pip install numpy pandas matplotlib
```

### 2. Run the Code
- Clone the repository to your local system:
```bash
git clone https://github.com/Cong-Lingzhi/reactionAnalyse.git
```
- Navigate to the repository directory:
```bash
cd reactionAnalyse
```
- Run the main program:
```bash
python main.py
```

## Code Structure
reactionAnalyse/
│
├── data/                 # Directory for raw data files
│
├── src/                  # Source code directory
│   ├── preprocess.py     # Data preprocessing module
│   ├── analysis.py       # Reaction analysis module
│   └── visualize.py      # Result visualization module
│
├── data.py               # data infos
├── main.py               # Main program entry
└── README.md             # Project documentation file

## Contributing
This work is supported by the National Science Foundation of China under Grant No. 12172112, 52293372, 11932005, and 11974091, and the National Natural Science Foundation of China (Joint Fund for Corporate Innovation and Development - Key Program) Grant no. U22B2082. And we would like to thank the National Key Laboratory of Space Environment and Matter Behaviors for their support throughout the project.

## License
This project is licensed under the MIT License.
