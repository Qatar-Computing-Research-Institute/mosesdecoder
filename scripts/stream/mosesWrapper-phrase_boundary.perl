#!/usr/bin/perl
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';


my $rN = rand();

my $input_file = "input.$rN.txt";
my $output_file = "$input_file.amirapbc.segs.txt";
my $decoder_output = "decoder_output.$rN.txt";
my $alignmentFile = "$input_file.amirapbc.ids.txt";
my $decoder_bin= "/work/moses-2013-09-05/bin/moses";

open(my $fh, '>:encoding(UTF-8)', $input_file);

foreach $line ( <STDIN> ) {
    chomp( $line );
    print $fh "$line\n";
}

# here write your program/code to chunk the file as 

# your_program < $input_file > $output_file;
# this program should also output mapping file with the format for example following program splits based on commas

#system("perl /home/users0/durrani/durrani-15/Stream-Decoding/scripts/punSplit.perl $rN < $input_file > $output_file");

system("perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$input_file");
system("python /work/stream/scripts/getPB-LEX.py $input_file.amirapbc");
#system("perl /home/users0/durrani/durrani-15/Stream-Decoding/scripts/countSplit.perl $rN 7 < $input_file > $output_file");

#system("cp $output_file $decoder_output");


$num_args = $#ARGV + 1;
$path_to_moses_decoder = $decoder_bin;
$cmd = $path_to_moses_decoder;

for (my $i=0; $i < $num_args; $i++)
{

	$path_to_moses_decoder = $path_to_moses_decoder . " " . $ARGV[$i];
	
}

$path_to_moses_decoder = $path_to_moses_decoder . " < " . $output_file . " > " . $decoder_output;

#print "$path_to_moses_decoder\n\n";

system("$path_to_moses_decoder");

	
	open(my $fh, '<:encoding(UTF-8)', $decoder_output) or die "Can't open $decoder_output for read: $!";


	while (<$fh>) {
	    chomp( $_ );
	    push (@lines, $_);
	}
	
	close $fh or die "Cannot close $decoder_output: $!";

	

	open(my $fh, '<:encoding(UTF-8)', $alignmentFile)
	   or die "Could not open file '$alignmentFile' $!";

	my $j = 0;
        my $output;

   	while (my $row = <$fh>) {
 		 chomp $row;

		$output = "";
		
		while ( $j <= $row)
		{
		  
		 $output = $output . $lines[$j]; 
		  $j++;
		}
	
	
		print "$output\n";
	}
 
