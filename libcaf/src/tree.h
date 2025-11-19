#ifndef TREE_H
#define TREE_H

#include <map>
#include <string>
#include <utility>

#include "tree_record.h"

class Tree {
public:
    using RecordMap = std::map<std::string, TreeRecord>;

    const RecordMap records;

    explicit Tree(const RecordMap& records): records(records) {}

    RecordMap::const_iterator record(const std::string& key) const {
        return records.find(key);
    }
};

#endif // TREE_H

