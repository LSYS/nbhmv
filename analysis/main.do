cap log close
local myLog "local log ../results/logs/full-log"
`myLog'
display "`myLog'"
log using `log'.smcl, replace smcl

* =========================================================
* Init
* =========================================================
do code/init/set_environment.do
tictoc tic 1

do code/init/set_globals.do

global SCRATCH 0
do code/init/data_preamble.do

// keep if _n in 1/5000
* =========================================================
* Nbh flows and mismatch
* =========================================================
do code/mismatch/pxor_wpsm.do
do code/mismatch/pxor_wpsm_r2p_p2r.do


tictoc toc 1
beepme 5

log close
`myLog'
translate `log'.smcl `log'.log, replace linesize(150)
translate `log'.smcl `log'.pdf, replace
