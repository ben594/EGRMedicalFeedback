# test algorithm based on recursive equation in https://www.proquest.com/docview/230725657?fromopenview=true&pq-origsite=gscholar&parentSessionId=W1kMUlbGIOWNRCDnOmr7ZIiBreMlbr1k0L7jFS3UGzY%3D

d = 3
b_0 = 0.18661
b_m = 0.07464
m = 3
a_1 = 0.74082

previous_map_diff = 0
infusion_rate = []
for i in range(0, 50):
    infusion_rate.append(5)
# t = 7
for t in range(7, 50):
    map_diff = b_0 * infusion_rate[t - d] + b_m * infusion_rate[t - d - m] + a_1 * previous_map_diff
    previous_map_diff = map_diff
    print(map_diff)