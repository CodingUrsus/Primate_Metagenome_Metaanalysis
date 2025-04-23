import sys
import os
import argparse  # For command-line argument parsing

def parse_fasta(filename):
    """Parses a FASTA file and returns a dictionary of {sequence_id: sequence}."""

    sequences = {}
    with open(filename, 'r') as file:
        current_id = None
        current_seq = ""
        for line in file:
            line = line.strip()
            if line.startswith(">"):  # New sequence header
                if current_id:
                    sequences[current_id] = current_seq
                current_id = line[1:]  # Remove ">"
                current_seq = ""
            else:
                current_seq += line
        if current_id:  # Add the last sequence
            sequences[current_id] = current_seq
    return sequences

def parse_cluster_file(filename):
    clusters = {}
    with open(filename, 'r') as file:
        for line in file:
            values = line.strip().split("\t")  # Split the line into a list of values
            if len(values) >= 2:
                gene, cluster_id = values[:2]  # Extract gene and cluster ID
                clusters.setdefault(cluster_id, []).append(gene)
    return clusters

def write_cluster_sequences(clusters, sequence_dict, output_dir):
    """Writes cluster sequences to separate files."""
    for cluster_id, genes in clusters.items():
        cluster_sequences = []
        for gene in genes:
            if gene in sequence_dict:
                cluster_sequences.append(f">{gene}\n{sequence_dict[gene]}")

        if cluster_sequences:  # Only write if there are sequences
            outfile_name = os.path.join(output_dir, f"{cluster_id}.faa")
            with open(outfile_name, 'w') as outfile:
                outfile.write("\n".join(cluster_sequences) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract FASTA sequences by cluster membership.")
    parser.add_argument("fasta_file", help="Path to the FASTA file.")
    parser.add_argument("cluster_file", help="Path to the cluster membership file.")
    parser.add_argument("output_dir", help="Directory to write the cluster FASTA files.")
    args = parser.parse_args()

    if not os.path.exists(args.fasta_file):
        print(f"Error: FASTA file '{args.fasta_file}' not found.")
        sys.exit(1)
    if not os.path.exists(args.cluster_file):
        print(f"Error: Cluster file '{args.cluster_file}' not found.")
        sys.exit(1)
    os.makedirs(args.output_dir, exist_ok=True)  # Create output directory if it doesn't exist

    sequence_dict = parse_fasta(args.fasta_file)
    clusters = parse_cluster_file(args.cluster_file)
    write_cluster_sequences(clusters, sequence_dict, args.output_dir)
