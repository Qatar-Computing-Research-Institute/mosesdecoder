#!/usr/bin/perl
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';

my $input_file = "$ARGV[0]";
my $key_file = "$ARGV[1]";

#open file
open(my $fh, '<:encoding(UTF-8)', $input_file) or die "Can't open $input_file for read: $!";


while (<$fh>) {
    chomp( $_ );
    push (@lines, $_);
}

close $fh or die "Cannot close $input_file: $!";


open($fh, '<:encoding(UTF-8)', $key_file)
   or die "Could not open file '$key_file' $!";

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
 
