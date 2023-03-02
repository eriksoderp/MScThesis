echo "This is a plot bash script"
while getopts i:s:l:p:c:d:t:o: flag
do
	case "${flag}" in
		i) input_file=${OPTARG};;
		s) number_of_sequences=${OPTARG};;
		l) number_of_letters=${OPTARG};;
    p) number_of_cores=${OPTARG};;
		o) outputfile=${OPTARG};;
		c) min_count=${OPTARG};;
		d) depth=${OPTARG};;
		t) threshold=${OPTARG};;
	esac
done
python3 modify_par.py -i $input_file -s $number_of_sequences -l $number_of_letters -p $number_of_cores -o "$outputfile.fna";
echo "Converting sequences to VLMCs";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold $threshold -o "${outputfile}_trees.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees.h5" -s "${outputfile}_dists.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists.h5" > "${outputfile}_dists.csv";
echo "Generating plot";
python3 new_plot_vlmc_ev.py modified_sequences/"distances_${outputfile}.csv" "${outputfile}_dists.csv" "figures/${outputfile}.png";
