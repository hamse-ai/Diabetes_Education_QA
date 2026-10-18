# Deployment notes

## Current status

The app is deployed at [diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app](https://diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app/). The project owner reports that the live app is working. It uses an 88 MB local checkpoint and candidate answers whose source, currentness, and safety review is incomplete. The interface identifies this clearly; deployment does not constitute clinical validation.

## Deployment configuration

The repository layout follows Streamlit Community Cloud's documented layout: a root `requirements.txt`, root `.streamlit/config.toml`, and an app entry point at `app/streamlit_app.py` [1]. The deployed app uses:

- Repository: `hamse-ai/Diabetes_Education_QA`
- Branch: `main`
- Entrypoint: `app/streamlit_app.py`
- Python: 3.13, matching the training environment as closely as the host allows [2]
- Public URL: [diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app](https://diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app/)

The repository owner must grant the Streamlit account access to the repo; deployment requires admin access to it [3]. Keep the prominent academic-prototype disclaimer visible.

## References

1. Streamlit Docs. [File organization for Community Cloud apps](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) and [app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
2. Streamlit Docs. [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
3. Streamlit Docs. [Connect your GitHub account](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account).
