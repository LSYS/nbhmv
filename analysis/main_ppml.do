cap log close
local myLog "local log ./logs/main_ppml"
`myLog'
display "`myLog'"

do code/init/set_environment.do
tictoc tic 1
do code/init/set_globals.do
do code/init/set_globals_ppml.do
do code/init/data_preamble_ppml.do

global graphsavedir ../results/figures/ppml/
global tabsavedir   ../results/tables/ppml/

set matsize 11000

do code/mismatch/pxor_wpsm_count_ppml.do
// do code/mismatch/pxor_wpsm_r2p_p2r_count_ppml.do
// do code/mismatch/pxor_race_count_ppml.do
// do code/mismatch/pxor_race_asymmetry_count_ppml.do

tictoc toc 1
beepme 5
