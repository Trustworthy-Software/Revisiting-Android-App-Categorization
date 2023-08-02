<div align="center">
  <h1 align="center">Revisiting Android App Categorization</h1>
</div>

In this repository, we host all the data and code related to our paper titled **Revisiting Android App Categorization**.

### 🗂️ Repository Organization

The repository mainly consists of Python code, with a significant number of Jupyter Notebooks.

The repository is organized according to the research questions we defined in our paper, with a folder for each one of them, plus three folders regarding the dataset:

- **0_Data**: Contains the ground-truth dataset ***AndroCatSet***, as well as all the results of the research questions.
- **0_DatasetCreation**: Contains the code we used to create ***AndroCatSet***.
- **0_DatasetInsight**: Provides insights about ***AndroCatSet***.
- **RQ1**: Evaluation of Existing Approaches.
- **RQ2**: ***G-CatA***, our new description-based categorization approach.
- **RQ3**: Different APK representations from existing unrelated tools.
- **RQ4**: Improvements of APK-based categorization approach.
- **RQ5**: Improvements of ***CHABADA*** when ***G-CatA*** is used on top of it.

### 📋 Requirements

To execute the entire code, two API keys are required. They should be set in an environment file named *config.env* using the following names: **ANDROZOO_API_KEY** and **OPENAI_API_KEY**.

- 🗝️ **ANDROZOO_API_KEY**: This key is necessary to download apps from the *AndroZoo* Repository, as various operations on the APK files are performed "on-the-fly," such as app download, extraction, and deletion. It can be requested here: [https://androzoo.uni.lu/access](https://androzoo.uni.lu/access)

- 🗝️ **OPENAI_API_KEY**: This key is required to utilize the Embedding models from OpenAI through their official API ([https://platform.openai.com/overview](https://platform.openai.com/overview)).

## ⚙️ Usage

### Dataset Creation

### RQ1

### RQ2

### RQ3

### RQ4

### RQ5

### 📑 References

As our research involves evaluating existing categorization approaches and attempting to use different APK representations from unrelated existing tools, we extensively utilized the code provided by the authors of various papers. Below is a list of the papers from which we reused the code.