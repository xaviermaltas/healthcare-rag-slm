import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  message?: string;
}

export function LoadingIndicator({ message = 'Generant document...' }: LoadingIndicatorProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full shadow-2xl">
        <div className="flex flex-col items-center gap-4">
          {/* Animated spinner */}
          <div className="relative">
            <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-blue-100 rounded-full animate-pulse"></div>
            </div>
          </div>
          
          {/* Message */}
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {message}
            </h3>
            <p className="text-sm text-gray-600">
              Aquest procés pot trigar fins a 30 segons
            </p>
          </div>
          
          {/* Progress steps */}
          <div className="w-full mt-4 space-y-2">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span className="text-gray-700">Recuperant protocols clínics...</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-100"></div>
              <span className="text-gray-700">Processant amb el model de llenguatge...</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse delay-200"></div>
              <span className="text-gray-700">Codificant terminologia mèdica...</span>
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mt-4 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full animate-progress"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
