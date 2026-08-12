function total(count, ack_count, nack_count)
{
	return sprintf("%ld/%ld+%ld=%ld", count, ack_count, nack_count, ack_count + nack_count);
}

BEGIN {
	D_count = 0;
	Dack_count = 0;
	DackY_count = 0;
	Dnack_count = 0;
	DnackY_count = 0;
	G_count = 0;
	Gack_count = 0;
	GackY_count = 0;
	Gnack_count = 0;
	GnackY_count = 0;
	F_count = 0;
	Fack_count = 0;
	FackY_count = 0;
	Fnack_count = 0;
	FnackY_count = 0;
	fill_count = 0;
	fillY_count = 0;
}

/35=D/ { D_count++; if (match($0, /43=Y/)) DY_count++ }
/35=G/ { G_count++; if (match($0, /43=Y/)) GY_count++ }
/35=F/ { F_count++; if (match($0, /43=Y/)) FY_count++ }

/35=8/ && /150=0/ { Dack_count++; if (match($0, /43=Y/)) DackY_count++ }
/35=8/ && /150=8/ { Dnack_count++; if (match($0, /43=Y/)) DnackY_count++ }
/35=8/ && /150=5/ { Gack_count++; if (match($0, /43=Y/)) GackY_count++ }
/35=9/ && /434=2/ { Gnack_count++; if (match($0, /43=Y/)) GnackY_count++ }
/35=8/ && /150=4/ { Fack_count++; if (match($0, /43=Y/)) FackY_count++ }
/35=9/ && /434=1/ { Fnack_count++; if (match($0, /43=Y/)) FnackY_count++ }

/35=8/ && /150=(1|2)/ { fill_count++; if (match($0, /43=Y/)) fillY_count++ }

END {
	printf("%ld record(s) processed\n", NR)
	printf("Totals:\n");
	print "NOS:", total(D_count, Dack_count, Dnack_count), DY_count, DackY_count, DnackY_count;
	print "AMD:", total(G_count, Gack_count, Gnack_count), GY_count, GackY_count, GnackY_count;
	print "CXL:", total(F_count, Fack_count, Fnack_count), FY_count, FackY_count, FnackY_count;
	printf("FIL: %ld-%ld=%ld\n", fill_count, fillY_count, fill_count - fillY_count);
}
