import numpy as np


def read_file(file):
    with open("data/cap" + file + ".txt", "r") as f:
        header = f.readline()
        no_facilities = int(header.split()[0])
        no_customers = int(header.split()[1])
        facility_lines = []
        for _ in range(no_facilities):
            facility_lines.append(f.readline())

        facility_capacity = []
        facility_costs = []
        for i in facility_lines:
            facility_capacity.append(int(i.split()[0]))
            facility_costs.append(float(i.split()[1]))

        facility_capacity = np.array(facility_capacity, dtype=int)
        facility_costs = np.array(facility_costs, dtype=float)

        customer_demands = np.zeros(no_customers, dtype=int)
        allocation_cost = np.zeros((no_customers, no_facilities))

        customers_read = 0
        values_collected = 0  # how many cost values collected for current customer
        reading_demand = True  # next line to read is a demand line

        while customers_read < no_customers:
            line = f.readline()

            if reading_demand:
                # start of a new customer: this line is its demand
                customer_demands[customers_read] = int(line)
                reading_demand = False
            else:
                # continuation: this line has (more) cost values
                values = [float(i.strip()) for i in line.split()]
                for value in values:
                    allocation_cost[customers_read][values_collected] = value
                    values_collected += 1

                if values_collected > no_facilities:
                    raise ValueError("collected more cost values than facilities")

                if values_collected == no_facilities:
                    customers_read += 1
                    values_collected = 0
                    reading_demand = True

        return (
            no_facilities,
            no_customers,
            facility_capacity,
            facility_costs,
            customer_demands,
            allocation_cost,
        )
