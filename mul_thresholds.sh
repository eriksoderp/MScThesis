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
echo "Converting sequences to VLMCs 0.0";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold 0.0 -o "${outputfile}_trees_00.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees_00.h5" -s "${outputfile}_dists_00.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists_00.h5" > "${outputfile}_dists_00.csv";

echo "Converting sequences to VLMCs 0.5";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold 0.5 -o "${outputfile}_trees_05.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees_05.h5" -s "${outputfile}_dists_05.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists_05.h5" > "${outputfile}_dists_05.csv";l

echo "Converting sequences to VLMCs 1.2";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold 1.2 -o "${outputfile}_trees_12.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees_12.h5" -s "${outputfile}_dists_12.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists_12.h5" > "${outputfile}_dists_12.csv";
echo "Converting sequences to VLMCs 3.9075";
build/src/pst-batch-training modified_sequences/"$outputfile.fna" --min-count $min_count --max-depth $depth --threshold 3.9075 -o "${outputfile}_trees_39075.h5";
echo "Calculating VLMC distances";
build/src/calculate-distances -p "${outputfile}_trees_39075.h5" -s "${outputfile}_dists_39075.h5";
echo "Converting distances h5 to csv";
python3 hdf2csv.py "${outputfile}_dists_39075.h5" > "${outputfile}_dists_39075.csv";
echo "Generating plot";
python3 thresholds_plot.py modified_sequences/"distances_${outputfile}.csv" "${outputfile}_dists" "figures/${outputfile}.png";
