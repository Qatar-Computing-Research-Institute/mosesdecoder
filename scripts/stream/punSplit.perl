#!/usr/bin/perl
binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';


my @words;
my $alignmentFile = "mapping.$ARGV[$0].txt";

open FILE, "> $alignmentFile" or die $!;

my $count = 0;

foreach $line ( <STDIN> ) {
    chomp( $line );

  	
     @words = split( /\s+/, $line );	


	for (my $i = 0; $i <= $#words; $i++) { 

		print "$words[$i]";
		

		if ( ($words[$i] =~ /\?/ || $words[$i] =~ /\./  || $words[$i] =~ /-/ || $words[$i] =~ /,/) && $i != $#words ) {

		#( $words[$i] =~ /\?/) && $i != $#words)
			$count++;
			print "\n";
		}
		else
		{
			if ($i != $#words)
			{
			   print " ";
			}
		}
  		  
	} 	
	
	print FILE "$count\n";
	$count++;
	
	print "\n";
	
}

