## Stata utilities

My Stata miscellaneous `.ado` programs I use.

Pull into my local project directory:
```Bash
cd <project_path>

git clone https://github.com/LSYS/stata-utils.git
```

Then in the relevant/master `do` file, add:
```Stata
adopath ++ ./stata-utils
```
or 
```Stata
adopath ++ <project_path>/stata-utils
```

## Programs

* `setup.ado` sets up multiple required packages. 

    Simple example:
    ```Stata
    local req reghdfe coefplot addplot
    setup "`req'"
    ```
    
    <details>
    <summary>Example with a <em>stata-requirements.txt</em>.</summary>

    <i>stata-requirements.txt</i> as an example plain text file:
    ```text
    reghdfe 
    coefplot
    addplot
    ```    
    
    Read `stata-requirements.txt` into local macro
    ```Stata
    txt2macro stata-requirements.txt
    local req `r(mymacro)'
    ```    
    
    and install packages listed in `stata-requirements.txt`
    ```Stata
    setup "`req'"
    ```
    </details>
    
    (Works like `pip install -r requirements.txt`)
