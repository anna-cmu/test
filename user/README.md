git clone https://github.com/facebookresearch/ParlAI.git ~/ParlAI
cd ~/ParlAI ; python3 setup.py develop

pip3 install -r requirements.txt 
pip3 install torchtext
pip3 install geotext



# Display custom data

python3 parlai/scripts/display_data.py -t fromfile:parlaiformat --fromfile_datapath user/custom_data/gpb_data.txt
python3 parlai/scripts/display_data.py -t fromfile:parlaiformat --fromfile-datapath user/custom_data/gpb_data --fromfile-datatype-extension true


# Pretrained model (blender_90M)

python3 -m user.interactive_gpb -mf zoo:blender/blender_90M/model

# Finetuning model (blender_90M) with name

python3 -m parlai.scripts.train_model -mf zoo:blender/blender_90M/model -t fromfile:parlaiformat --fromfile_datapath user/custom_data/gpb_data1.txt --num_epochs 30 --numthreads -3

python3 -m user.interactive_gpb -mf zoo:blender/blender_90M/model

# Finetuning model (blender_90M) with name and age

python3 -m parlai.scripts.train_model -mf zoo:blender/blender_90M/model -t fromfile:parlaiformat --fromfile_datapath user/custom_data/gpb_data1.txt --num_epochs 30 --numthreads -3
python3 -m parlai.scripts.train_model -mf zoo:blender/blender_90M/model -t fromfile:parlaiformat --fromfile_datapath user/custom_data/gpb_data2.txt --num_epochs 50 --numthreads -1

python3 -m user.interactive_gpb -mf zoo:blender/blender_90M/model

# test_sub_chatbot
