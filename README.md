<div align="center">

  <h1 align="center">Revisiting Android App Categorization</h1>

  <p align="center"> Avilaible on Zenodo:
  </p>

  [![DOI](https://zenodo.org/badge/669074668.svg)](https://zenodo.org/doi/10.5281/zenodo.10378629)

  <p align="center">
    Paper Available:
    <br />
    <a href="https://doi.org/10.48550/arXiv.2310.07290"> <strong>[HERE]</strong></a>
    <br />
    <br />
    <a href="https://github.com/MarcoAlecci">Marco Alecci</a>
    ·
    <a href="https://www.jordansamhi.com/">Jordan Samhi</a>
    ·
    <a href="https://bissyande.github.io/">Tegawendé F. Bissyandé</a>
    ·
    <a href="https://jacquesklein2302.github.io/">Jacques Klein</a>
    ·
  </p>
</div>

# 📜 Abstract

>Numerous tools rely on automatic categorization of Android apps as part of their methodology. However, incorrect categorization can lead to inaccurate outcomes, such as a malware detector wrongly flagging a benign app as malicious. One such example is the SlideIT Free Keyboard app, which has over 500000 downloads on Google Play. Despite being a "Keyboard" app, it is often wrongly categorized alongside "Language" apps due to the app's description focusing heavily on language support, resulting in incorrect analysis outcomes, including mislabeling it as a potential malware when it is actually a benign app. Hence, there is a need to improve the categorization of Android apps to benefit all the tools relying on it. In this paper, we present a comprehensive evaluation of existing Android app categorization approaches using our new ground-truth dataset. Our evaluation demonstrates the notable superiority of approaches that utilize app descriptions over those solely relying on data extracted from the APK file, while also leaving space for potential improvement in the former category. Thus, we propose two innovative approaches that effectively outperform the performance of existing methods in both description-based and APK-based methodologies. Finally, by employing our novel description-based approach, we have successfully demonstrated that adopting a higher-performing categorization method can significantly benefit tools reliant on app categorization, leading to an improvement in their overall performance. This highlights the significance of developing advanced and efficient app categorization methodologies for improved results in software engineering tasks.

# ✏️ Citation

Please, cite our work:

```
@misc{alecci2023revisiting,
      title={Revisiting Android App Categorization}, 
      author={Marco Alecci and Jordan Samhi and Tegawendé F. Bissyandé and Jacques Klein},
      year={2023},
      eprint={2310.07290},
      archivePrefix={arXiv},
      primaryClass={cs.SE}
}
```

# 🎯 Purpose

The artifact associated with our paper possesses a dual nature,
comprising two main parts that can be classified as Non-executable and
Executable, respectively. The first part, denoted as
**AndroCatSet**, constitutes the non-executable segment. It is
the first ground-truth dataset for evaluating Android app categorization
methodologies, encompassing 5,000 apps categorized into 100 different
classes, such as Calculator, Translator, and others. The artifact's
second component contains all the code utilized in conducting our
experiments. This includes our newly developed description-based app
categorization approach named **G-CatA**.

<p align="center">
  <img src="https://i.postimg.cc/mzmD4df5/badgesClaimed.png" alt="Badges claimed." />
</p>

We claim the *Available* and *Reusable* badges. Regarding the *Available* badge, we ensured the availability of our artifact by storing the software source
code on Zenodo, thus guaranteeing its long-term accessibility. Regarding the *Reusable* badge, we have implemented extensive measures to enhance the reusability and adaptability of our code. The repository has been meticulously organized, complemented by comprehensive documentation and instructions explaining how to replicate the experiments and analyses conducted during the paper's composition. Additionally, we provide a `DockerFile`, ensuring a streamlined and consistent environment for reproducing our experiments. This accessibility ensures that our work is readily available for future researchers seeking to replicate or expand upon our experiments.
# 🔗 Provenance

The following links are provided:

-   Link to preprint: <https://arxiv.org/abs/2310.07290>

-   Link to public repository:
    <https://github.com/Trustworthy-Software/Revisiting-Android-App-Categorization>

-   Link to Zenodo:

In compliance with the ICSE 2024 Artifact Submission Guidelines, along
with the code and dataset, we have included the following documents to
provide guidance in the repository:

-   **readme.md** - A comprehensive guide detailing all scripts and
    directories, following a structure similar to this document and
    encompassing all the sections requested by the guideline.

-   **RevisitingAndroidAppCategorization.pdf** - A copy of our accepted
    paper.

-   **license.md** - Distribution rights (GNU GPL 3.0)

# 🗂️ Data

**AndroCatSet** is released as a CSV file, which helps in
saving memory storage since the CSV file weighs only 10.6 MB. All
experiments were conducted 'on the fly', with the APK files downloaded
from **AndroZoo** whenever necessary. The
methodology employed to construct **AndroCatSet** is
extensively described in our paper. It comprises five columns: sha256
(uniquely identifying the app), the assigned classID, package name,
Google Play Category ID, and the app's description.

Regarding the code, the repository (97,6 MB) mainly comprises Python
code, along with a significant number of Jupyter Notebooks. A
`Dockerfile` and a `docker-compose.yml` are also provided to improve
reproducibility.

The repository's structure aligns with the research questions outlined
in our paper, featuring a dedicated folder for each question, plus three
folders regarding the dataset. The organizational layout is as follows:

-   **Data**: Contains the ground-truth dataset
    **AndroCatSet**, as well as all the results of the
    research questions.

-   **DatasetCreation**: The code for **AndroCatSet**
    creation.

-   **DatasetInsight**: Provides insights about
    **AndroCatSet**.

-   **RQ1**: Evaluation of existing categorization approaches.

-   **RQ2**: **G-CatA**, our description-based categorization
    approach.

-   **RQ3**: APK representations from existing unrelated tools.

-   **RQ4**: Improvements of APK-based categorization approach.

-   **RQ5**: Improvements of CHABADA when
    **G-CatA** is used on top of it.

# 💻 Technology Skills Expected

We assume that the reviewer evaluating the artifact is familiar with
Python, Jupyter Notebooks, and Docker. Moreover, we suggest that they
read the documentation of the **AndroZoo**(https://androzoo.uni.lu/api_doc) and [OpenAI](https://platform.openai.com/docs/introduction) as these are frequently used in our code.

# 🛠️ Setup

In this section, we will explain how to prepare a '.env' file containing
the API keys and how to prepare the artifact for execution.

## 🔑 Environment File (.env)

To execute the entire code, two API keys are required: one for
AndroZoo and another for the OpenAI API. These keys should
be set in an environment file named *.env*, which should be placed in
the main folder of the provided repository.

The API Keys should be named **ANDROZOO_API_KEY** and
**OPENAI_API_KEY**.

-   **ANDROZOO_API_KEY**: This key is necessary to download apps from
    the *AndroZoo* Repository, as various operations on the APK files
    are performed \"on-the-fly,\" such as app download, extraction, and
    deletion. It can be requested here: <https://androzoo.uni.lu/access>

-   **OPENAI_API_KEY**: This key is required to utilize the Embedding
    models from OpenAI through their official API
    (<https://platform.openai.com/overview>).

## 🐋 Docker

In accordance with the ICSE 2024 Artifact Submission Guidelines, we have
created a `Dockerfile` and a `docker-compose.yml` to improve
reproducibility. To build the image and launch the container, users
should execute the following command:

    docker-compose up

Once running, the repository can be accessed at: <http://localhost:8888/>


You can access it using the token provided in the output of `compose`,
or by directly clicking the link generated by the `compose` output.

# ⚙️ Usage

In this section, we will explain how to verify if everything has been
set up correctly and how to run the experiments described in our paper.

## 🔧 Test Setup

After completing the setup phase described in the previous section, to
ensure everything is properly set up, we provide a Jupyter notebook in
the home folder of the repository (`testSetup.ipynb`). The notebook
attempts to load `datasetName` and verify the correct loading of API
Keys from the environment file. Then, using these two API Keys, tests
will be conducted using the **AndroZoo** API and the OpenAI
API.

## 🧪 Running the experiments

In the entire repository, there are 16 different categorization
approaches, each with a similar pipeline involving several phases such
as data extraction, preprocessing, embedding, and clustering. Given that
our dataset comprises 5000 apps, rerunning all the experiments for each
approach would be excessively time-consuming. Some of these approaches
could require up to 1 to 2 weeks for data extraction, especially those
relying on data extracted from the APK files. Additionally, it would be
quite expensive due to the OpenAI API being a paid service (Pricing
information can be found here: <https://openai.com/pricing>).

For this reason, we provide a smaller version of the
**AndroCatSet**, named `AndroCatSet_MiniTEST.csv`, which
contains 50 apps divided into 5 classes. This implies that it will not
be possible to generate the same plots included in the paper, and the
ARI score obtained will, of course, differ from the one obtained in the
paper, as the evaluation is conducted solely on 5 classes. However, this
smaller version can be used to prove that all the code is reusable.

The code is presented in Jupyter Notebooks to aid execution and
understanding. These notebooks are named and organized in sequence to
prevent potential errors in execution order. By running them in order,
it's possible to generate the final outcome i.e., a file containing the
clustering labels, without needing to worry about saving intermediate
files, as the notebooks will manage this automatically

The notebooks are currently configured to operate with the test version
of the dataset and categorize the apps into only five groups. However,
to completely rerun the entire experiment with the full dataset, it is
only necessary to change the `INPUT_PATH` variable at the beginning of
the first notebook for each approach and adjust the `NUM_CLUSTERS`
parameter from 5 to 50 in the final notebook of each approach. The
correct parameters are already present but are commented out, making it
easy to modify them.