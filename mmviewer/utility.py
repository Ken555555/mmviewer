#!/usr/bin/env python3
import os
from argparse import ArgumentParser
from __init__ import __version__

def get_option():
    super_argparser = ArgumentParser(
        prog='mmviewer',
        description='Missense Mutation Viewer (MMViewer) v' + str(__version__) + ' (K. IKebata, 2021)' 
    )
    super_argparser.add_argument(
        '-v', '--version', action='version', version='%(prog)s v'+ str(__version__)
    )
    sub_argparser = super_argparser.add_subparsers(
        dest='program_name',
        help="""First, run get_target program to get target.bed file and cds.gff file. \
            Second, run alignment program to get graph_config.csv file. \
            Third, run gen_graph program to generate graph."""
    )
    # definition of sub arg
    gt_argparser = sub_argparser.add_parser(
        'get_target', help='Run get_target program to get target.bed describing target region and cds.gff file.'
    )
    al_argparser = sub_argparser.add_parser(
        'alignment', help='Run alignment program to get bam files.'
    )
    gg_argparser = sub_argparser.add_parser(
        'gen_graph', help='Run gen_graph program to generate mutation graph.'
    )
    # Set gt_argparser
    rq_gt_group = gt_argparser.add_argument_group('required arguments')
    op_gt_group = gt_argparser.add_argument_group('graph region (optional)')
    rq_gt_group.add_argument(
        '-c', '--complete_seq', type=str, required=True, 
        help='Path to a file of complete genome or contig in fasta format as a reference. (required)'
    )
    rq_gt_group.add_argument(
        '-g', '--gene_sequence', type=str, required=True, 
        help='Path to a file of target gene in fasta format. (required)'
    )
    rq_gt_group.add_argument(
        '-o', '--output', type=str, required=True, 
        help='Output directory. (required)'
    )
    rq_gt_group.add_argument(
        '-t',  '--gene_seq_type', type=str, default='prot', choices=['nucl', 'prot'], required=True,
        help='A type of gene_sequence file (nucleotide or animo acid), default = prot. (optional)'
    )
    op_gt_group.add_argument(
        '-u', '--upper_interval', type=int, required=False, default=0, metavar='0',
        help='The bp number of additional upper region from cds, defaults to 0. (optional)'
    )
    op_gt_group.add_argument(
        '-l', '--lower_interval', type=int, required=False, default=0, metavar='0',
        help='The bp number of additional lower region from cds, you want to analyze, defaults to 0. (optional)'
    )
    # Set al_argparser
    rq_al_group = al_argparser.add_argument_group('required arguments')
    rq_al_group.add_argument(
        '-a', '--alignment_config_file', type=str, required=True,
        help='''Alignment_config.csv file consists of 2 or 3 columns with a header in first row.
            1st column: sample name.
            2nd column: path to trimmed read file in fastq format or its compressed format (.gz).
            3rd column (option): path to trimmed read file in fastq format or its compressed format (.gz) of reverse reads if paired end read.'''
    )
    rq_al_group.add_argument(
        '-c', '--complete_seq', type=str, required=True, 
        help='Path to a file of complete genome or contig in fasta format as a reference. (required)'
    )
    rq_al_group.add_argument(
        '-o', '--output', type=str, required=True, 
        help='Output directory. (required)'
    )
    # Set gg_argparser
    rq_gg_group = gg_argparser.add_argument_group('required arguments')
    op_gg_group = gg_argparser.add_argument_group('optional arguments')
    rq_gg_group.add_argument(
        '-c', '--complete_seq', type=str, required=True,
        help='Path to a file of complete genome or contig in fasta format as a reference. (required)'
    )
    rq_gg_group.add_argument(
        '-o', '--output', type=str, required=True,
        help='Output directory. (required)'
    )
    rq_gg_group.add_argument(
        '-a', '--graph_config', type=str, required=True,
        help="""Path to graph_config.csv file generated by \'mmviewer alignment\'. 
            It consists of sample_name column and bam file path column with header in first row.
            Sample order of output graph follows the order in this file."""
    )
    rq_gg_group.add_argument(
        '-b', '--target_bed', type=str, required=True,
        help="""Path to target.bed file generated by \'mmviewer get_target\'. 
            It consists of 8 columns (chrom, chromStart, chromEnd, name, score, strand, CDS_Start, CDS_End).
            Users can edit this file.
            If the values in name column are same, regions in these rows will be shown in the same graph sheet.
            """
    )
    rq_gg_group.add_argument(
        '-d', '--cds_gff', type=str, required=True,
        help='Path to cds.gff file generated by \'mmviewer get_target\'.'
    )
    op_gg_group.add_argument(
        '-p', '--min_depth', type=int, required=False, default=5, metavar='5',
        help='Minimum depth of reads as a mapped region. (default=5)'
    )
    return super_argparser.parse_args()

def make_directory(dir_name, out_dir):
    """Make new directory and confirm that there's no same directy name.
    If new file_name already exist, add '_1' at the last.

    :param dir_name: new directory name 
    :type file_name: str
    :param out_dir: path to directory where you want to put the new directory
    :type out_dir: str
    :return: path to new directory
    :rtype: str
    """
    i=0
    tmp_dir=os.path.join(out_dir, dir_name)
    while True:
        if not os.path.isdir(tmp_dir):
            break
        else:
            i += 1
            tmp_dir = os.path.join(out_dir, dir_name + '_' + str(i))
    if os.path.join(out_dir, dir_name) != tmp_dir:
        print('warning! ' + out_dir + ' already exist!')
        print(tmp_dir + ' was generated instead.')
    os.mkdir(tmp_dir)
    return tmp_dir

def make_dir_files(dir_name, out_dir, prefix_list, ext):
    """Make new directory and generate files path list

    :param dir_name: new directory name 
    :type file_name: str
    :param out_dir: path to directory where you want to put the new directory
    :type out_dir: str
    :param prefix_list: prefix list of files
    :type prefix_list: list
    :param ext: file extension (e.g. '.txt')
    :type ext: str
    :return: directory name, file list
    :rtype: (str, list)
    """
    i=0
    tmp_dir=os.path.join(out_dir, dir_name)
    while True:
        if not os.path.isdir(tmp_dir):
            break
        else:
            i += 1
            tmp_dir = os.path.join(out_dir, dir_name + '_' + str(i))
    if os.path.join(out_dir, dir_name) != tmp_dir:
        print('warning! ' + out_dir + ' already exist!')
        print(tmp_dir + ' was generated instead.')
    os.mkdir(tmp_dir)
    files = [os.path.join(tmp_dir, ll + ext) for ll in prefix_list]
    return tmp_dir, files