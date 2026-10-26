cap log close
local myLog "local log ./logs/main_strict_ms50_asymtest"
`myLog'
display "`myLog'"

* Reruns only the directional tables, after switching the asymmetry test
* from x1 + x2 = 0 to x1 = x2 (editor's final check, Oct 2026)

do code/init/set_environment.do
global STRICT_TAG "ms50"
tictoc tic 1
do code/init/set_globals.do
do code/init/data_preamble.do

* Tab E33, E35
do code/mismatch/pxor_wpsm_r2p_p2r.do
do code/mismatch/pxor_race_asymmetry.do

tictoc toc 1
beepme 5
