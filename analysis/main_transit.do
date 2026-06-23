cap log close
local myLog "local log ./logs/main_transit"
`myLog'
display "`myLog'"

do code/init/set_environment.do
tictoc tic 1
do code/init/set_globals.do
do code/init/data_preamble.do

cap mkdir ../results/figures/transit
cap mkdir ../results/tables/transit
global graphsavedir ../results/figures/transit/
global tabsavedir   ../results/tables/transit/

do code/transit_time_robustness/pxor_wpsm_transit.do
do code/transit_time_robustness/pxor_wpsm_r2p_p2r_transit.do
do code/transit_time_robustness/pxor_race_transit.do
do code/transit_time_robustness/pxor_race_asymmetry_transit.do

tictoc toc 1
beepme 5
