cap program drop tables2in1
program define tables2in1
    // =============================================================================
    /* This program outputs two different versions of regression reports.

      MWE:
      ----
      sysuse auto, clear

      eststo clear
      eststo: reg price mpg
      eststo: reg price mpg length
      tables2in1 2, savepath(_)
    */
    // =============================================================================
// Syntax --------------------------------------------------------------------------
   syntax anything, ///
      [xlabel(string)] /// Variable label for main estimand
      [keep(string asis)] /// Variables to report
      [coeflabels(string asis)] /// Dict of variable labels
      [var(string asis)] /// Variable (for replacement in the wide format)
      [scalars(string asis)] /// Open-ended options for scalar indicators
      [savepath(string asis)] /// Savepath
      [star(string asis)] /// Format stat. sig. (default = * 0.1 ** 0.05 *** 0.01)
      [bformat(string)] /// Numeric format of estimates (default = %9.3f)
      [seformat(string)] /// Numeric format of SE (default = %9.3f)
      [ciformat(string)] /// Numeric format of confidence bounds (default = %9.3f)
      [pformat(string)] /// Numeric format of p-values (default = %4.3f)
      [OPTs_esttab(string asis)] /// Open-ended esttab/estout options

   version 13.1

   if "`bformat'"=="" local bformat %9.3f
   if "`ciformat'"=="" local ciformat %9.3f
   if "`pformat'"=="" local pformat %4.3f
   if "`star'"=="" local star c 0.1 b 0.05 a 0.01
   if `"`savepath'"'!="" {
      local savepathwide `savepath'
      local savepath using `"`savepath'"'
   }
   else if "`savepath'"=="" {
      local savepath 
      local savepathwide 
   }
   // Version 1
   #delimit;
   esttab `savepath',
   cell(
      b (                   fmt(`bformat') star) 
      se(par                fmt(`seformat'))
      ci(par(\multicolumn{1}{r}{\text{[$ \text{--} $]}}) fmt(`ciformat'))
      p (par(\multicolumn{1}{r}{\text{$<p= >$}})           fmt(`pformat')) 
        )      
   keep(`keep')
   coeflabels(`coeflabels')
   collabels(, none) /// needed to remove the b/../... label below column header
   nonumber /// suppresses column numbers
   nomtitle /// suppresses printing of model titles
   noobs /// suppresses observation report
   star(`star')
   scalar(`scalars')
   sfmt(%9.2f)
   // Other LaTeX settings
   fragment /// suppresses tabular environment headers
   substitute(\_ _)
   `opts_esttab'
   booktab
   replace
   ;
   #delimit cr     

   // Version 2 (wide) --- each model is a row saved in a separate file
   local models `anything'
   forvalues m = 1/`models' {
      #delimit; 
      esttab est`m' using `savepathwide'-wide-`m',
         cell(
            b(fmt(`bformat')) & 
            se(fmt(`seformat')) & 
            ci(par(\multicolumn{1}{r}{\text{[$ \text{--} $]}}) fmt(`ciformat')) &
            p(fmt(`pformat'))
         )
         incelldelimiter(&) /// delimit using "&" so tex recognizes as columns 
         collabels(, none) /// needed to remove the b/../... label below column header
         noconstant /// suppresses reporting of constant
         keep(`keep')
         noobs /// suppresses observation report
         plain
         coeflabels(`var' "Model `m'")
         nomtitle /// suppresses printing of model titles
         // Other LaTeX settings
         fragment /// suppresses tabular environment headers   
         substitute(\_ _)
         booktab
         `opts_esttab'
         replace
         ;#delimit cr   
      }
end
// End -----------------------------------------------------------------------------

