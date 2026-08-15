cap log close
local myLog "local log ./logs/main_strict_ms50"
`myLog'
display "`myLog'"

do code/init/set_environment.do
global STRICT_TAG "ms50"
tictoc tic 1
do code/init/set_globals.do
do code/init/data_preamble.do

do code/mismatch/pxor_wpsm.do
do code/mismatch/pxor_wpsm_r2p_p2r.do
do code/mismatch/pxor_race.do
do code/mismatch/pxor_race_asymmetry.do

tictoc toc 1
beepme 5
