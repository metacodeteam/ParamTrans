# ParamTrans
The source code and dataset for ParamTrans.

### Python libraries needed for ParamTrans
#### For data processing：
anytree
javalang

#### For model traning and testing:

numpy
tqdm
nltk
prettytable
torch>=1.3.0


### DataProcessing
We generate our parameter summary dataset from the filtered CoDesc dataset(file filter.json in the share link) based on the script in the DataProcessing folder, including our algorithm for extracting parameter-level ASTs.





### Dataset
Our dataset is available in the [Google Drive](https://drive.google.com/drive/folders/1U-J3AciK2HlpH_d-NFGoWKurDAEfATDw?usp=drive_link).
To train the model with the dataset we created, you can copy the contents of the dataset folder to the /data/java folder of the model.


### Training/Testing Models
We provide the implement of all of our models in the paper, including ParamTrans,Serial-ParamTrans,Parallel-ParamTrans and Flat-ParamTrans.

To train and test the model,fisrt:

Go to the folder of a model,like Flat-ParamTrans.

```
$ cd Flat-ParamTrans
```

Go to the script folder:


```
$ cd  scripts/java
```


Then run the script as:

```
$ bash transformer.sh GPU_ID MODEL_NAME
```

GPU_ID specifies the GPU used to run the experiment, you can use one or more GPUs to run the experiment, when multiple GPUs are specified, the GPU ids are separated by commas.
If you want  to run the experiment by CPU, set the GPU_ID to -1.

MODEL_NAME is the name used when saving the model and the results.

For example:

```
$ bash transformer.sh 0,1 paramtrans
```


You can modify the parameters in the script file to adjust the hyperparameters and to enable and disable Copy Attention and Split Decoder.



