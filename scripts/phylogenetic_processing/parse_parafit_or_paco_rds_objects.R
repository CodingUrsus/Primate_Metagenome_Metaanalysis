#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

file_location <- args[1]
out_location <- args[2]
test_type <- args[3] ## must be "paco" or "parafit"

list_of_files <- list.files(file_location, full.names=T)


read_paco <- function(some_num, file_list){
  myobj <- readRDS(file_list[some_num])
  mydim <- dim(myobj$HP)
  return(c(mydim[1], mydim[2], myobj$gof$p, file_list[some_num]))
}

read_parafit <- function(vector_iterator, list_of_parafit){
  my_parafit <- readRDS(list_of_parafit[vector_iterator])
  parafit_pval <- my_parafit$p.global
  return(c(list_of_parafit[vector_iterator], parafit_pval))
}

if (test_type=="paco"){
  paco_pvals <- data.frame(sapply(1:length(list_of_files), function(x) read_paco(x, list_of_files)))
  paco_outlocation <- paste0(out_location, "paco_test_results.rds")
  saveRDS(paco_pvals, paco_outlocation)
} else if (test_type=="parafit"){
  parafit_pvals <- data.frame(sapply(1:length(list_of_files), function(x) read_parafit(x, list_of_files)))
  parafit_outlocation <- paste0(out_location, "parafit_test_results.rds")
  saveRDS(parafit_pvals, parafit_outlocation)
} else{
  print("Test type to parse not specified! Check the test type requirement in the script")
}

