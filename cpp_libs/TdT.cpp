#include <vector>
#include <string>
#include <random>
#include <cstring>
#include <map>

std::mt19937 gen(std::random_device{}());
std::uniform_real_distribution<double> dis(0.0, 1.0);

std::map<int, char *> dataMap;
int currentId = 0;

void freeMemoryInternal(int id) {
    if (dataMap.find(id) != dataMap.end()) {
        delete[] dataMap[id];
        dataMap.erase(id);
    }
}

extern "C"
{

    int weighted_random_exclusive(double probability0, double probability1) {
        double r = dis(gen);
        if (r < probability0) {
            return 0;
        } else if (r < probability0 + probability1) {
            return 1;
        } else {
            return -1;
        }
    }

    bool weighted_random(double probability) {
        return dis(gen) < probability;
    }

    int extension(const char *base_cstr, double miss_extension_probability, int reaction_cycle, const char *bases_list_cstr) {
        std::string base(base_cstr);
        std::string bases_list(bases_list_cstr);
        std::string result;

        for (int i = 0; i < reaction_cycle; ++i) {
            std::string ext_base = base;
            if (weighted_random(miss_extension_probability)) {
                std::string other_bases = "";
                for (char b : bases_list) {
                    if (b != base[0]) {
                        other_bases += b;
                    }
                }
                if (!other_bases.empty()) {
                    ext_base = other_bases[gen() % other_bases.size()];
                }
            }

            int deletion_or_over = weighted_random_exclusive(0.2, 0.1);
            if (deletion_or_over == -1) {
                result += ext_base;
            } else if (deletion_or_over == 0) {
                result += ext_base + ext_base;
            } else if (deletion_or_over == 1) {                
            }
        }

        char *cstr_result = new char[result.size() + 1];
        std::strcpy(cstr_result, result.c_str());
        int id = currentId++;
        dataMap[id] = cstr_result;
        return id;
    }

    int synthesis(const char *target_base_cstr, double miss_extension_probability, int reaction_cycle, const char *bases_list_cstr, int molecule_number) {
        std::string target_base(target_base_cstr);
        std::string bases_list(bases_list_cstr);
        std::string synthesis_result;

        for (int i = 0; i < molecule_number; ++i) {
            for (char base : target_base) {
                int ext_id = extension(&base, miss_extension_probability, reaction_cycle, bases_list_cstr);
                char *extended_bases = dataMap[ext_id];
                synthesis_result += extended_bases;
                freeMemoryInternal(ext_id);
            }
            synthesis_result += ';';
        }

        char *cstr_result = new char[synthesis_result.size() + 1];
        std::strcpy(cstr_result, synthesis_result.c_str());
        int id = currentId++;
        dataMap[id] = cstr_result;
        return id;
    }

    void free_memory(int id) {
        freeMemoryInternal(id);
    }
    
    char* get_data_pointer(int id) {
        auto it = dataMap.find(id);
        if (it != dataMap.end()) {
            return it->second;
        }
        return nullptr;
    }
}
