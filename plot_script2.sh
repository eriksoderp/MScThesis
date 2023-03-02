echo "This is a plot bash script"
while getopts c:d:t:n:o: flag
do
	case "${flag}" in
		o) outputfile=${OPTARG};;
		c) min_count=${OPTARG};;
		d) depth=${OPTARG};;
		t) threshold=${OPTARG};;
        n) number=${OPTARG};;
	esac
done
echo "Converting sequences to VLMCs";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold $threshold -o "${outputfile}_trees_${number}.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees_${number}.h5" -s "${outputfile}_dists_${number}.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists_${number}.h5" > "${outputfile}_dists_${number}.csv";
echo "Generating plot";
python3 plot_ev_vlmc.py modified_sequences/"distances_${outputfile}.csv" "${outputfile}_dists_${number}.csv" "figures/${outputfile}_${number}.png";
