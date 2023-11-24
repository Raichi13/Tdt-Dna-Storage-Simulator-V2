#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <cstring>
#include <cmath>

std::vector<std::string> removeDnaRepeat(const std::vector<std::string>& dna) {
    std::vector<std::string> result;
    std::string last_base = "";
    for (const auto& base : dna) {
        if (base != last_base) {
            result.push_back(base);
        }
        last_base = base;
    }
    return result;
}

std::vector<std::string> buildConsensusBase(const std::vector<std::vector<std::string>>& dna_sequences) {
    int totalLength = 0;
    for (const auto& seq : dna_sequences) {
        totalLength += seq.size();
    }
    int avgLength = static_cast<int>(std::round(static_cast<double>(totalLength) / dna_sequences.size()));

    std::vector<std::string> consensus;
    for (size_t i = 0; i < avgLength; ++i) {
        std::unordered_map<std::string, int> frequency;
        for (const auto& seq : dna_sequences) {
            if (i < seq.size()) {
                frequency[seq[i]]++;
            }
        }

        int maxFreq = 0;
        std::vector<std::string> mostFreqBases;
        for (const auto& pair : frequency) {
            if (pair.second > maxFreq) {
                maxFreq = pair.second;
                mostFreqBases.clear();
                mostFreqBases.push_back(pair.first);
            } else if (pair.second == maxFreq) {
                mostFreqBases.push_back(pair.first);
            }
        }

        if (!mostFreqBases.empty()) {
            consensus.push_back(mostFreqBases[0]);
        }
    }

    return consensus;
}

extern "C" {
    char* getConsensusSequence(char** sequences, int num_sequences, int* sequence_lengths) {
        std::vector<std::vector<std::string>> dna_sequences(num_sequences);
        for (int i = 0; i < num_sequences; ++i) {
            dna_sequences[i].reserve(sequence_lengths[i]);
            for (int j = 0; j < sequence_lengths[i]; ++j) {
                dna_sequences[i].push_back(std::string(1, sequences[i][j]));
            }
            dna_sequences[i] = removeDnaRepeat(dna_sequences[i]);
        }

        std::vector<std::string> consensus = buildConsensusBase(dna_sequences);
        std::string consensus_str;
        for (const auto& base : consensus) {
            consensus_str += base;
        }

        char* cstr = new char[consensus_str.length() + 1];
        std::strcpy(cstr, consensus_str.c_str());
        return cstr;
    }

    void free_consensus_sequence(char* sequence) {
        delete[] sequence;
    }
}