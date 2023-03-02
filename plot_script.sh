echo "This is a plot bash script"
while getopts i:s:l:c:d:t:o: flag
do
	case "${flag}" in
		i) input_file=${OPTARG};;
		s) number_of_sequences=${OPTARG};;
		l) number_of_letters=${OPTARG};;
		o) outputfile=${OPTARG};;
		c) min_count=${OPTARG};;
		d) depth=${OPTARG};;
		t) threshold=${OPTARG};;
	esac
done
python3 modify.py -i $input_file -s $number_of_sequences -l $number_of_letters -o "$outputfile.fna";
echo "Converting sequences to VLMCs";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold $threshold -o "${outputfile}_trees.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees.h5" -s "${outputfile}_dists.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists.h5" > "${outputfile}_dists.csv";
echo "Generating plot";
python3 plot_ev_vlmc.py modified_sequences/"distances_${outputfile}.csv" "${outputfile}_dists.csv" "figures/${outputfile}.png";
