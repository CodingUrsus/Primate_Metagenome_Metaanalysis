#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

# Rscript /raid1/home/micro/hammera/scripts/test_parafit_and_paco.R /raid1/home/micro/hammera/more_trees /raid1/home/micro/hammera

main_tree_dir <- args[1]
out_location <- args[2]

#main_tree_dir <- "/home/micro/hammera/test_trees"
#out_location <- "/raid1/home/micro/hammera/paco_parafit_results/"


library(stringr)
library(phytools)
library(ape)
library(phangorn)
library(dplyr)
library(purrr)
library(paco)
library(parallel)
primate_host_tree <- read.tree("/raid1/home/micro/hammera/host_taxa.nwk")


create_empty_table <- function(num_rows, num_cols) {
    frame <- data.frame(matrix(NA, nrow = num_rows, ncol = num_cols))
    return(frame)
}

test_parafit <- function(snoops_tree, your_host_tree, tree_name, out_dir){
  print(snoops_tree)
  gc()
  host_tree <- your_host_tree
  protein_tree <- read.tree(snoops_tree)
  tip_labs <- (protein_tree$tip.label)
  split_df <- str_split(tip_labs, "_", n = 3, simplify = FALSE)
  first_name <- t(as.data.frame(map(split_df, 1)))
  second_name <- t(as.data.frame(map(split_df, 2)))
  final_names <- paste0(first_name[,1], "_", second_name[,1])
  tips_to_drop <- host_tree$tip.label[!(host_tree$tip.label %in% final_names)]
  final_host_tree <- drop.tip(host_tree, tips_to_drop)
  host_dist <- cophenetic.phylo(final_host_tree)
  protein_dist <- cophenetic.phylo(protein_tree)
  first_df <- create_empty_table(num_rows = length(final_host_tree$tip.label), num_cols = length(protein_tree$tip.label))
  base_col <- numeric(length(protein_tree$tip.label))
  host_names <- final_host_tree$tip.label
  paratein_names <- protein_tree$tip.label
  for(i in 1:length(paratein_names)) {
    for (j in 1:length(host_names)){
      if(grepl(host_names[j], paratein_names[i])){
        first_df[j, i] <- 1
      } 
      else {
        first_df[j, i] <- 0
      }
    }
  }
  colnames(first_df) <- paratein_names
  rownames(first_df) <- host_names
  
  Paco_obj <- prepare_paco_data(host_dist, protein_dist, first_df)
  Paco_obj <- add_pcoord(Paco_obj, correction="cailliez")
  paco_res <- try({PACo(Paco_obj, nperm=2000, method="r0", symmetric=FALSE)})
  if (class(paco_res)!="try-error"){
    paco_file_name <- paste0(out_dir, tree_name, "_paco_results.rds")
    saveRDS(paco_res, paco_file_name)
    paco_pval <- paco_res$gof$p
  }
  else{
    paco_pval <- "NA"
  }
  put_it_all_together <- try({parafit(host_dist, protein_dist, first_df, nperm=10000, correction="cailliez")}, silent=TRUE)
  if (class(put_it_all_together)!="try-error") {
    parafit_file_name <- paste0(out_dir, tree_name, "_parafit_results.rds")
    saveRDS(put_it_all_together, parafit_file_name)
	return(c(tree_name, put_it_all_together$p.global, paco_pval))}
  else {
	return (tree_name, "NA", paco_pval)}
}

file_list <- list.files(main_tree_dir, pattern=".nwk", full.names = TRUE)
partial_file_list <- list.files(main_tree_dir, pattern=".nwk", full.names = F)

CL <- makeCluster(40)
clusterEvalQ(CL, {library(ape)
  library(stringr)
  library(phytools)
  library(ape)
  library(phangorn)
  library(dplyr)
  library(purrr)
  library(paco)})
clusterExport(cl=CL, c('test_parafit', 'create_empty_table', 'file_list', 'primate_host_tree', 'partial_file_list', 'out_location'))
ptm <- proc.time()
testsapply <- parSapply(cl=CL, 1:length(file_list), function(i) test_parafit(file_list[i],primate_host_tree, partial_file_list[i], out_location))
print(proc.time()-ptm)

## stop cluster running. remember to run this if there's an error in the sapply function
stopCluster(CL)

#file_out <- paste0(out_location, "/parafit_and_paco_test_results.rds")

#saveRDS(testsapply, file_out)


