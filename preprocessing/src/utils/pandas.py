import pandas as pd
import copy

class DataFrameWithName(pd.DataFrame):
    # normal properties
    _metadata = ['metadata_df_name']

    @property
    def _constructor(self):
        return DataFrameWithName
    
def put_df_name(df, name):
    df = DataFrameWithName(df)
    df.metadata_df_name = name
    return df