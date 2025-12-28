import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useNeed, useUpdateNeed } from '@/hooks/useNeeds';
import { useCommunity } from '@/contexts/CommunityContext';
import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { VisibilitySelector } from '@/components/VisibilitySelector';
import { RESOURCE_CATEGORIES, COMMON_UNITS, COMMON_LOCATIONS } from '@/utils/categories';
import { validateIntentForm } from '@/utils/validation';
import { ArrowLeft } from 'lucide-react';

export function EditNeedPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: need, isLoading: loadingNeed } = useNeed(id!);
  const updateNeed = useUpdateNeed();
  const { currentCommunity } = useCommunity();
  const { user, isAuthenticated, loading } = useAuth();

  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [item, setItem] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('kg');
  const [location, setLocation] = useState('');
  const [availableFrom, setAvailableFrom] = useState('');
  const [availableUntil, setAvailableUntil] = useState('');
  const [note, setNote] = useState('');
  const [visibility, setVisibility] = useState<'my_cell' | 'my_community' | 'trusted_network' | 'anyone_local' | 'network_wide'>('trusted_network');
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);

  // Populate form when need loads
  useEffect(() => {
    if (need) {
      setItem(need.resource_spec_id || '');
      setQuantity(need.quantity?.toString() || '');
      setUnit(need.unit || 'kg');
      setLocation(need.location_id || '');
      setAvailableFrom(need.available_from ? new Date(need.available_from).toISOString().split('T')[0] : '');
      setAvailableUntil(need.available_until ? new Date(need.available_until).toISOString().split('T')[0] : '');
      setNote(need.description || '');
      setVisibility((need.visibility as any) || 'trusted_network');
    }
  }, [need]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login?redirect=/needs');
    }
  }, [loading, isAuthenticated, navigate]);

  // Don't render if not authenticated or not the owner
  if (loading || loadingNeed) {
    return <div className="max-w-2xl mx-auto p-8 text-center">Loading...</div>;
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  if (!need) {
    return (
      <div className="max-w-2xl mx-auto p-8 text-center">
        <ErrorMessage message="Need not found" />
        <Button onClick={() => navigate('/needs')} className="mt-4">
          Back to Needs
        </Button>
      </div>
    );
  }

  // Check ownership
  if (need.agent_id !== user.id) {
    return (
      <div className="max-w-2xl mx-auto p-8 text-center">
        <ErrorMessage message="You can only edit your own needs" />
        <Button onClick={() => navigate('/needs')} className="mt-4">
          Back to Needs
        </Button>
      </div>
    );
  }

  const selectedCategory = RESOURCE_CATEGORIES.find(cat => cat.id === category);
  const subcategories = selectedCategory?.subcategories || [];
  const selectedSubcategory = subcategories.find(sub => sub.id === subcategory);
  const items = selectedSubcategory?.items || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    const resourceName = item || `${category}/${subcategory}`;

    const validation = validateIntentForm({
      resourceSpecificationId: resourceName,
      quantity: parseFloat(quantity),
      unit,
      location,
    });

    if (!validation.valid) {
      setErrors(validation.errors);
      return;
    }

    // Validate date range
    if (availableFrom && availableUntil) {
      const fromDate = new Date(availableFrom);
      const untilDate = new Date(availableUntil);

      if (untilDate <= fromDate) {
        setErrors(['"Needed Until" must be after "Needed From"']);
        return;
      }
    }

    try {
      await updateNeed.mutateAsync({
        id: id!,
        data: {
          resource_spec_id: resourceName,
          quantity: parseFloat(quantity),
          unit,
          location_id: location || undefined,
          available_from: availableFrom || undefined,
          available_until: availableUntil || undefined,
          description: note || undefined,
          visibility,
        },
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/needs');
      }, 1500);
    } catch (error) {
      setErrors(['Failed to update need. Please try again.']);
    }
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="confirmation success-message bg-green-50 border-l-4 border-green-500 p-6 rounded-lg">
          <h2 className="text-2xl font-bold text-green-900 mb-2">✓ Need Updated!</h2>
          <p className="text-green-700 mb-4">Your need has been updated successfully!</p>
          <p className="text-sm text-gray-600 mt-4">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Edit Need</h1>
        <p className="text-gray-600 mt-1">Update your need details</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {errors.length > 0 && (
            <ErrorMessage message={errors.join(', ')} />
          )}

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">What do you need?</h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  setSubcategory('');
                  setItem('');
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a category...</option>
                {RESOURCE_CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {category && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subcategory *
                </label>
                <select
                  value={subcategory}
                  onChange={(e) => {
                    setSubcategory(e.target.value);
                    setItem('');
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select a subcategory...</option>
                  {subcategories.map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {subcategory && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Item *
                </label>
                <select
                  value={item}
                  onChange={(e) => setItem(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select an item...</option>
                  {items.map((itm) => (
                    <option key={itm} value={itm}>
                      {itm}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit *
              </label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                {COMMON_UNITS.map((u) => (
                  <option key={u} value={u}>
                    {u}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">No specific location</option>
              {COMMON_LOCATIONS.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Needed From
              </label>
              <input
                type="date"
                value={availableFrom}
                onChange={(e) => setAvailableFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Needed Until
              </label>
              <input
                type="date"
                value={availableUntil}
                onChange={(e) => setAvailableUntil(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <VisibilitySelector
            value={visibility}
            onChange={(val) => setVisibility(val as any)}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any additional details about this need..."
            />
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(-1)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateNeed.isPending}
              className="flex-1"
            >
              {updateNeed.isPending ? 'Updating...' : 'Update Need'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
