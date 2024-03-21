#!/bin/bash

# Specify dependency in the following format:
# "github_folder_path,ref;target_dir"
deps=("YousefGh/kmeans-feature-importance.git/kmeans_interp,kmeans-feature-importance-v01;kmeans_feature_importance")

for spec in "${deps[@]}"; do
    # Split target directory and github path
    github_ref="${spec%%;*}"
    target_dir="${spec#*;}"

    github_path="${github_ref%%,*}"
    github_ref="${github_ref#*,}"

    # Get the GitHub repo name
    repo_name="${github_path%%.git*}.git"

    # Get the folder path
    folder_path="${github_path#*.git/}"

    dst_path=deps/$target_dir

    echo "Cloning $repo_name ref $github_ref folder $folder_path to $dst_path"

    # clone folder from git repo to temporary directory
    rm -rf deps/tmp
    rm -rf $dst_path
    git clone https://github.com/$repo_name deps/tmp

    cd deps/tmp
    git checkout $github_ref
    cd -

    mv deps/tmp/$folder_path $dst_path
    rm -rf deps/tmp
done
