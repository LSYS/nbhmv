local base i.date##i.pa_origin i.date##i.pa_dest

local s1 `base'
foreach v in $dist $popden $landarea {
    local s1 `s1' i.date#c.`v'
}
global s1_ppml `s1'

* s2 = s1 + demo
local s2 `s1'
foreach v in $demo {
    local s2 `s2' i.date#c.`v'
}
global s2_ppml `s2'

* s3 = s2 + business
local s3 `s2'
foreach v in $business {
    local s3 `s3' i.date#c.`v'
}
global s3_ppml `s3'

* s4 = s3 + rain
local s4 `s3'
foreach v in $rain {
    local s4 `s4' i.date#c.`v'
}
global s4_ppml `s4'

* s5 = s4 + poi
local s5 `s4'
foreach v in $poi {
    local s5 `s5' i.date#c.`v'
}
global s5_ppml `s5'

assert_macros "s1_ppml s2_ppml s3_ppml s4_ppml s5_ppml"
