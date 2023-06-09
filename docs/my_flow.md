# Overview Of My Experience Building This

---

## Getting Started

I created this project and the files/directories as I saw best fit my needs. Lots of placeholders.

First I installed all the required libraries with pip, conda, etc.

Next I work on creating the **`settings.py`** file. This file will contain all the configuration settings for the LLMs and the deployment environment.

* First I decided to review the Runhouse setup docs. Runhouse encourages you to run `sky check`
* This exposes that many of the default cloud environemnts are not configured due to various reasons:
  * **GCP:** *"GCP tools are not installed or credentials are not set. Run the following commands:"*
    * **`pip install google-api-python-client`**
    * **`conda install -c conda-forge google-cloud-sdk -y`**
    * **`gcloud init`**
    * **`gcloud auth application-default login`**
  * **AWS:** *"AWS credentials are not set. Run the following commands:"*
    * **`pip install boto3`**
    * **`aws configure`**
    * **`aws configure list # ensure this shows identity is set.`**
  * **Azure:** *" ~/.azure/msal_token_cache.json does not exist. Run the following commands"*
    * **`pip install azure-cli`**
    * **`az login`**
    * **`az account set -s <subscription_id>`**
  * **Lambda, IBM, Cloudflare** (omitted for brevity)
* Ensure to update **`bashrc/bashprofile`** **`$PATH`** to include necessary paths.
* **`runhouse login`** to sync secrets and update runhouse account.
* How to setup paperspace ... here's an example from tutorials repo:
  * To bring your own GPU (e.g. if you have a Paperspace or Coreweave account), you can run:
```python
rh.cluster(ips=['<ip of the cluster>'], 
           ssh_creds={'ssh_user': '...', 'ssh_private_key':'<path_to_key>'},
           name='rh-a10x').save()
```
  * Looks like we need:
    * IP of cluster
    * SSH credentials (user and private key)
    * Name of cluster




