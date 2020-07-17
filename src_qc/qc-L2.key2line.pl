=head1
    Author: Hua Sun
    Email: hua.sun@wustl.edu/hua.sun229@gmail.com
    Date: 8/30/2019 v0.8
    only for qc-L2 version

=head1 USAGE

    -lc [int]      #list col
    -cc [int]      #content col
    -keyN [int]    #select continuous 1-5 col based on -lc & -cc
    -showListAll   #show whole lists
    -showList      #show lists when the keys shared between list and content files
    -o [str]       #output

    -uniq          # if find duplicated ID, it will get the first value.

    perl key2line.pl -cut list.txt content.txt -o out
    perl key2line.pl -lc 1 -cc 2 -keyN 2 -showList -showListAll list.txt content.txt -o out
    perl key2line.pl -lc 1 -cc 2 -keyN 2 -showList -showListAll -uniq list.txt content.txt -o out
    
  #ex. list.txt
  ID1
  ID2
  ...

  #ex. content.txt
  Des. ID1 ID2 ...
  ...

=cut


use strict;
use Tie::File;
use Tie::Hash;
use Getopt::Long;


my $l_col=1;
my $c_col=1;
my $keyN=1;  #- key col 1 or 2 or 3
my $show_list;
my $show_all_list;
my $out;

my $cutCol;     #----- do cut column
my $sortbyCol;  #----- do output by column

our $UNIQ;
my $fuzzy; 

my $Help;
GetOptions(
    "lc:i"=>\$l_col,
    "cc:i"=>\$c_col,
    "keyN:i"=>\$keyN,
    "showList"=>\$show_list,
    "showListAll"=>\$show_all_list,
    "o:s"=>\$out,
    "cutCol"=>\$cutCol,
    "sortbyCol" => \$sortbyCol,
    "uniq" => \$UNIQ,
    "fuzzy" => \$fuzzy,
    "help"=>\$Help
);

die `pod2text $0` if (@ARGV==0 || $Help || !$out);

my ($listF, $contentF)=@ARGV;

## Check file
die "[ERROR] No $listF\n" unless (-e $listF);
die "[ERROR] No $contentF\n" unless (-e $contentF);


##------------------------ Handle as column
# output as cut col

# output as sort by col



##------------------------ Handle as row

##=========================##
##    Accurate matching
##=========================##
# read content

our %HashCon;   #------------------- save content
tie %HashCon, 'Tie::StdHash';
our $NA;        #------------------- for empty col.
&ReadContent($contentF, $c_col, $keyN);
system "echo INFO: Finshed to read content file...";


# output by list
unless (defined $fuzzy){

    open my ($IN_LIST),'<',$listF;
    open OUT,">$out";

    --$l_col;
    my $key;
    my $content;
    foreach my $str (<$IN_LIST>) {
        chomp($str);
        next if ($str eq '');
        
        #- remove space; sometimes miss typing to add space
        $str =~ s/ +\t/\t/g;
        $str =~ s/\t +/\t/g;
        $str =~ s/ +$//;
        $str =~ s/^ +//;
        
        my @arr=split("\t",$str);
        
        # set numbers of columns as key
        $key = &CleanKey($arr[$l_col]);
        
        if ($keyN == 2) {
            $key.=":".&CleanKey($arr[$l_col+1]);
        }
        if ($keyN == 3) {
            $key.=':'.&CleanKey($arr[$l_col+1]).':'.&CleanKey($arr[$l_col+2]);
        }
        if ($keyN == 4) {
            $key.=':'.&CleanKey($arr[$l_col+1]).':'.&CleanKey($arr[$l_col+2]).':'.&CleanKey($arr[$l_col+3]);
        }
        if ($keyN == 5) {
            $key.=':'.&CleanKey($arr[$l_col+1]).':'.&CleanKey($arr[$l_col+2]).':'.&CleanKey($arr[$l_col+3]).':'.&CleanKey($arr[$l_col+4]);
        }       
        
        # output based on keys
        if (exists $HashCon{$key}) {
            $content=$HashCon{$key};
            if ($show_list || $show_all_list) {
                if ($content =~ /\n/){
                    my @temp = split("\n", $content);
                    foreach my $x_str(@temp){
                        print OUT "$str\t$x_str\n";  #------ out multiple content
                    }
                } else {
                    print OUT "$str\t$content\n";  #------ list content
                }
            } else {
                print OUT "$content\n";
            }
        } else {
            if ($show_all_list) {  #-------------- if no matched then input 'NA'
                print OUT "$str\t$NA\n";
            }
        }

    }
    close OUT;
}




# close big data hash file
untie %HashCon or die "Could not close file!\n";


exit;



########################################################
##        remove ^ & $ space for get accurate key
########################################################
sub CleanKey
{
    my $k = shift;
    
    $k =~ s/^ +//;
    $k =~ s/ +$//;
    
    return $k;
}



########################################################
##          Extract by column
########################################################


########################################################
##          sort by column based on list
########################################################


########################################################
##          Read content by row
########################################################
sub ReadContent
{
    my ($conF,$col,$keyN)=@_;

    --$col;
    
    # save fa to temp. file by chr.
    tie my @bigData, 'Tie::File', "$conF" or die "Could't open file!";  #read big data


#   open my ($IN),'<',$conF;
    my $key;
    my $totalCol;
    foreach my $str (@bigData) {
        chomp($str);
        my @arr=split("\t",$str);

        $totalCol=@arr; #-for 'NA'

        $key=&CleanKey($arr[$col]);
        
        next if ($key eq '');

        if ($keyN == 2) {
            $key.=":".&CleanKey($arr[$col+1]);
        }
        if ($keyN == 3) {
            $key.=':'.&CleanKey($arr[$col+1]).':'.&CleanKey($arr[$col+2]);
        }
        if ($keyN == 4) {
            $key.=':'.&CleanKey($arr[$col+1]).':'.&CleanKey($arr[$col+2]).':'.&CleanKey($arr[$col+3]);
        }
        if ($keyN == 5) {
            $key.=':'.&CleanKey($arr[$col+1]).':'.&CleanKey($arr[$col+2]).':'.&CleanKey($arr[$col+3]).':'.&CleanKey($arr[$col+4]);
        }       
                
        # add 
        if (exists $HashCon{$key}) {
            next if (defined $UNIQ);   #--if set the -uniq, then do next
            $HashCon{$key}.="\n$str";  #--duplicated id seperated by '\n'
        } else {
            $HashCon{$key}=$str;
        }
    }

    #--- for making empty col. using N/A
    $NA='';
    foreach my $i (1..$totalCol) {
        $NA.="NA\t";
    }
    $NA=substr($NA,0,-1);
    
    
    # close big data file
    untie @bigData or die "Could not close file!\n";
}



