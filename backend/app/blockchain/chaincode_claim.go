// chaincode_claim.go
package main

import (
	"encoding/json"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type Claim struct {
	ID         string  `json:"id"`
	Country    string  `json:"country"`
	OwnerHash  string  `json:"owner_hash"`
	Amount     float64 `json:"amount"`
	Status     string  `json:"status"`
	Commission float64 `json:"commission"`
}

type SmartContract struct {
	contractapi.Contract
}

func (s *SmartContract) RecordClaim(ctx contractapi.TransactionContextInterface, claimJSON string) error {
	var claim Claim
	err := json.Unmarshal([]byte(claimJSON), &claim)
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(claim.ID, []byte(claimJSON))
}
