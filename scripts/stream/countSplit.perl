#!/usr/bin/perl
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';


my @words;
my $alignmentFile = "mapping.$ARGV[0].txt";
my $wCount = $ARGV[1];

open FILE, "> $alignmentFile" or die $!;

my $count = 0;

foreach $line ( <STDIN> ) {
    chomp( $line );

  	
     @words = split( /\s+/, $line );	


	my $flag;

	for (my $i = $wCount+1; $i <= $#words + $wCount +1; $i++) { 


		print "$words[$i-$wCount-1] ";
		$flag = 0;
		
		if ($i % $wCount == 0)
		{
			$count++;
			print "\n";
			$flag = 1;
		}
  		  
	} 	
	
	if ($flag == 1)
	{
		$count--;
	}
	else
	{
		 print "\n";
	}

	print FILE "$count\n";
	$count++;	
		
}

