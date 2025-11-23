import { useState, useEffect } from 'react';
import { getHashChain, verifyHashChain, verifyBlockchain } from '../lib/api';

const HashChain = () => {
  const [hashChainEntries, setHashChainEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    loadHashChain();
  }, []);

  const loadHashChain = async () => {
    try {
      setLoading(true);
      const data = await getHashChain(100);
      setHashChainEntries(data);
      setError(null);
    } catch (err) {
      console.error('Error loading hash chain:', err);
      setError(err.message || 'Failed to load hash chain');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    try {
      setVerifying(true);
      const result = await verifyHashChain();
      setVerificationResult(result);
    } catch (err) {
      console.error('Error verifying hash chain:', err);
      setError(err.message || 'Failed to verify hash chain');
    } finally {
      setVerifying(false);
    }
  };

  const handleVerifyBlockchain = async (txHash) => {
    if (!txHash) return;
    try {
      const result = await verifyBlockchain(txHash);
      alert(`Blockchain Verification:\n${JSON.stringify(result, null, 2)}`);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateHash = (hash, length = 16) => {
    if (!hash) return 'N/A';
    if (hash.length <= length) return hash;
    return `${hash.substring(0, length)}...`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#7FFF00] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading hash chain...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-fadeIn">
          <h1 className="text-4xl font-bold text-[#222123] mb-2">Hash Chain & Blockchain</h1>
          <p className="text-gray-600 text-lg">Immutable audit trail of all predictions</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">{hashChainEntries.length}</p>
              <p className="text-sm text-gray-600 mt-1">Total Entries</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">
                {hashChainEntries.filter(e => e.blockchain_tx_hash).length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Blockchain Commits</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">
                {verificationResult?.valid ? '✓' : verificationResult ? '✗' : '-'}
              </p>
              <p className="text-sm text-gray-600 mt-1">Chain Integrity</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">
                {hashChainEntries.filter(e => e.blockchain_tx_hash && e.blockchain_tx_hash.startsWith('0x')).length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Simulated TXs</p>
            </div>
          </div>
        </div>

        {/* Verify Button */}
        <div className="mb-6 flex justify-center">
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="px-8 py-3 bg-[#7FFF00] text-black rounded-lg hover:bg-[#6ee000] transition-colors font-bold border-2 border-[#222123] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {verifying ? 'Verifying...' : 'Verify Hash Chain Integrity'}
          </button>
        </div>

        {/* Verification Result */}
        {verificationResult && (
          <div className={`mb-6 p-6 rounded-xl border-2 shadow-lg animate-fadeIn ${
            verificationResult.valid 
              ? 'bg-green-50 border-green-300' 
              : 'bg-red-50 border-red-300'
          }`}>
            <h3 className="text-xl font-bold mb-2">
              {verificationResult.valid ? '✓ Chain is Valid' : '✗ Chain Verification Failed'}
            </h3>
            <p className="text-sm text-gray-700">{verificationResult.message}</p>
            {verificationResult.total_entries && (
              <p className="text-sm text-gray-600 mt-2">
                Total entries verified: {verificationResult.total_entries}
              </p>
            )}
            {verificationResult.errors && verificationResult.errors.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-semibold text-red-600 mb-2">
                  Errors ({verificationResult.errors.length}):
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                  {verificationResult.errors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-6 bg-red-50 border-2 border-red-300 rounded-xl shadow-lg animate-fadeIn">
            <p className="text-red-600 font-semibold">Error: {error}</p>
          </div>
        )}

        {/* Hash Chain Entries */}
        <div className="space-y-4">
          {hashChainEntries.length === 0 ? (
            <div className="bg-white rounded-xl p-8 border-2 border-[#222123] shadow-lg text-center">
              <p className="text-gray-500">No hash chain entries found</p>
            </div>
          ) : (
            hashChainEntries.map((entry, index) => (
              <div
                key={entry.id}
                className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg hover:shadow-xl transition-shadow animate-fadeIn"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-[#222123] mb-2">
                      Entry #{entry.id} {index === 0 && <span className="text-sm text-gray-500">(Latest)</span>}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Prediction: {truncateHash(entry.prediction_id, 30)}
                    </p>
                    {entry.prediction && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        <span className="px-2 py-1 bg-[#7FFF00] bg-opacity-20 text-[#222123] rounded text-xs font-semibold">
                          {entry.prediction.predicted_disease || 'Unknown'}
                        </span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          {entry.prediction.source}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">{formatDate(entry.block_timestamp)}</p>
                  </div>
                </div>

                {/* Hash Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs font-semibold text-gray-600 mb-1">Current Hash</p>
                    <p className="text-sm font-mono text-[#222123] break-all">
                      {truncateHash(entry.current_hash, 40)}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs font-semibold text-gray-600 mb-1">Previous Hash</p>
                    <p className="text-sm font-mono text-[#222123] break-all">
                      {entry.previous_hash ? truncateHash(entry.previous_hash, 40) : 'Genesis (First Entry)'}
                    </p>
                  </div>
                </div>

                {/* Blockchain Info */}
                {entry.blockchain_tx_hash ? (
                  <div className="bg-[#7FFF00] bg-opacity-10 rounded-lg p-4 border-2 border-[#7FFF00]">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold text-gray-600 mb-1">Blockchain Transaction</p>
                        <p className="text-sm font-mono text-[#222123] break-all mb-2">
                          {truncateHash(entry.blockchain_tx_hash, 30)}
                        </p>
                        {entry.blockchain_block_number && (
                          <p className="text-xs text-gray-600">
                            Block: {entry.blockchain_block_number}
                          </p>
                        )}
                        {entry.blockchain_tx_hash.startsWith('0x') && entry.blockchain_tx_hash.length < 20 && (
                          <p className="text-xs text-[#7FFF00] font-semibold mt-1">
                            ⚠️ Simulated Transaction
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleVerifyBlockchain(entry.blockchain_tx_hash)}
                        className="px-4 py-2 bg-[#7FFF00] text-black rounded-lg hover:bg-[#6ee000] transition-colors font-bold text-xs border-2 border-[#222123]"
                      >
                        Verify
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-100 rounded-lg p-4 border-2 border-gray-300">
                    <p className="text-xs text-gray-600">Not yet committed to blockchain</p>
                  </div>
                )}

                {/* Full Hash on Hover */}
                <details className="mt-4">
                  <summary className="text-sm text-gray-600 cursor-pointer hover:text-[#7FFF00]">
                    View Full Details
                  </summary>
                  <div className="mt-2 space-y-2 text-xs">
                    <div>
                      <span className="font-semibold">Current Hash:</span>
                      <p className="font-mono text-gray-700 break-all">{entry.current_hash}</p>
                    </div>
                    {entry.previous_hash && (
                      <div>
                        <span className="font-semibold">Previous Hash:</span>
                        <p className="font-mono text-gray-700 break-all">{entry.previous_hash}</p>
                      </div>
                    )}
                    {entry.blockchain_tx_hash && (
                      <div>
                        <span className="font-semibold">TX Hash:</span>
                        <p className="font-mono text-gray-700 break-all">{entry.blockchain_tx_hash}</p>
                      </div>
                    )}
                    <div>
                      <span className="font-semibold">Created:</span>
                      <p className="text-gray-700">{formatDate(entry.created_at)}</p>
                    </div>
                  </div>
                </details>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default HashChain;

