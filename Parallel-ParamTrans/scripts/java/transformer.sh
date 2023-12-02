#!/usr/bin/env bash


function make_dir () {
    if [[ ! -d "$1" ]]; then
        mkdir $1
    fi
}

SRC_DIR=../..
DATA_DIR=${SRC_DIR}/data
MODEL_DIR=${SRC_DIR}/tmp

make_dir $MODEL_DIR

DATASET=java

function train () {

echo "============TRAINING============"


RGPU=$1
MODEL_NAME=$2

PYTHONPATH=$SRC_DIR CUDA_VISIBLE_DEVICES=$RGPU python -W ignore ${SRC_DIR}/main/train.py \
--data_workers 5 \
--dataset_name java \
--data_dir ${DATA_DIR}/ \
--model_dir $MODEL_DIR \
--model_name $MODEL_NAME \
--train_src train/train.sbt \
--train_src2 train/train.method.nl \
--train_tgt train/train.nl \
--dev_src dev/valid.sbt \
--dev_src2 dev/valid.method.nl \
--dev_tgt dev/valid.nl \
--uncase True \
--use_src_word True \
--use_src_char False \
--use_tgt_word True \
--use_tgt_char False \
--max_src_len 150 \
--max_tgt_len 50 \
--emsize 512 \
--fix_embeddings False \
--src_vocab_size 50000 \
--src2_vocab_size 50000 \
--tgt_vocab_size 30000 \
--share_decoder_embeddings True \
--max_examples -1 \
--batch_size 64 \
--test_batch_size 128 \
--num_epochs 200 \
--model_type transformer \
--num_head 8 \
--d_k 64 \
--d_v 64 \
--d_ff 2048 \
--src_pos_emb False \
--tgt_pos_emb True \
--max_relative_pos 32 \
--use_neg_dist True \
--nlayers 6 \
--trans_drop 0.2 \
--dropout_emb 0.2 \
--dropout 0.2 \
--copy_attn True \
--early_stop 20 \
--warmup_steps 2000 \
--optimizer adam \
--learning_rate 0.0001 \
--lr_decay 0.99 \
--valid_metric bleu \
--checkpoint True \
--split_decoder False
}

function test () {

echo "============TESTING============"

RGPU=$1
MODEL_NAME=$2

PYTHONPATH=$SRC_DIR CUDA_VISIBLE_DEVICES=$RGPU python -W ignore ${SRC_DIR}/main/train.py \
--only_test True \
--data_workers 5 \
--dataset_name $DATASET \
--data_dir ${DATA_DIR}/ \
--model_dir $MODEL_DIR \
--model_name $MODEL_NAME \
--dev_src test/test.sbt \
--dev_src2 test/test.method.nl \
--dev_tgt test/test.nl \
--uncase True \
--max_src_len 150 \
--max_tgt_len 50 \
--max_examples -1 \
--test_batch_size 128

}



train $1 $2
test $1 $2

