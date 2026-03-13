import os
import io
import pandas as pd

# The Bot pulls the secret from the GitHub "Vault" 
# and turns it into a virtual file in memory
secret_data = os.getenv("FLOWER_ANSWERS") 

# This creates a dataframe without ever saving a file on the disk
truth = pd.read_csv(io.StringIO(secret_data), names=['original_filename', 'label'])
