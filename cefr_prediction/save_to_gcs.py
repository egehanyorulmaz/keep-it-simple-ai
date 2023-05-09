from helpers.gcs_funcs import upload_blob


upload_blob(bucket_name = "kisai-data-msca310019-capstone",
            source_file_name = "/home/jupyter/keep-it-simple-ai/cefr_prediction/cefr_ktrain_bert/tf_model.h5",
            destination_blob_name = "CEFR/models/tf_model.h5")

upload_blob(bucket_name = "kisai-data-msca310019-capstone",
            source_file_name = "/home/jupyter/keep-it-simple-ai/cefr_prediction/cefr_ktrain_bert/tf_model.preproc",
            destination_blob_name = "CEFR/models/tf_model.preproc")
