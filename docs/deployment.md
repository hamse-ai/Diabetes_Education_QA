# Deployment notes

## Current status

The Streamlit application and dependency manifest are prepared, but there is no public deployment URL yet. The app uses an 88 MB local checkpoint and a candidate answer set whose source, currentness, and safety review is incomplete. The interface identifies this clearly. Do not present the deployment as a validated health service.

## Streamlit Community Cloud setup

The repository layout follows Streamlit Community Cloud's documented layout: a root `requirements.txt`, root `.streamlit/config.toml`, and an app entry point at `app/streamlit_app.py` [1]. After the repository is available on GitHub:

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and create an app.
2. Select the GitHub repository, its `main` branch, and `app/streamlit_app.py` as the entry point [2].
3. In Advanced settings, select Python 3.13 to match the training environment as closely as the host allows. Community Cloud currently defaults to Python 3.12, so this selection matters for dependency compatibility [2].
4. Deploy and inspect the app logs. The app needs the repository's model checkpoint and review files to remain included.
5. Open the public URL and demonstrate general information, a source link, a low-evidence abstention, and personal/emergency boundary handling.

The repository owner must grant the Streamlit account access to the repo; deployment requires admin access to it [3]. Keep the prominent academic-prototype disclaimer visible.

## References

1. Streamlit Docs. [File organization for Community Cloud apps](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) and [app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
2. Streamlit Docs. [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
3. Streamlit Docs. [Connect your GitHub account](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account).
